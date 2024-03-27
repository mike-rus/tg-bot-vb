import os
import json
import logging
from typing import List
import asyncio
import datetime

from telegram.ext._utils.types import BT
from telegram.ext._jobqueue import JobQueue, Job
from telegram.ext import ApplicationBuilder, CallbackContext
from telegram._message import Message

from classes.club import Club
from classes.team import Team

logger = logging.getLogger(__name__)


# The task of the class is to store information about clubs, perform basic bot routines, and unload local data to restore the bot's operation after a reboot.
class ChatRegistry:
    def __init__(self, registry_folder: str):
        """
        Initializes the ChatRegistry object.

        Args:
            registry_folder (str): The path to the folder where registry files are stored.
        """
        self.clubs: List[Club] = []
        self.jobs: List[Job] = []
        self.job_idx: int = 1
        self.registry_folder = registry_folder

        # Create registry folder if it does not exist
        if not os.path.exists(self.registry_folder):
            os.makedirs(self.registry_folder)
        else:
            # Restore registry if folder already exists
            self._registry_restoration()

    async def add_club(self, club: Club):
        """
        Adds a new club to the registry.

        Args:
            club (Club): The Club object to be added.
        """
        if not self._is_new_chat_id(club.get_chat_id()):
            # If the club already exists, send a message indicating it
            await self.send_message(
                chat_id=club.get_chat_id(),
                text=f"The club {club.get_title()} with id #{club.get_chat_id()} already exists",
                self_destruct=10,
            )
        else:
            # If the club is new, add it to the registry, send a registration message, and store the club data to file
            self.clubs.append(club)
            await self.send_message(
                chat_id=club.get_chat_id(),
                text=f"The club {club.get_title()} with id #{club.get_chat_id()} has been registered",
            )
            self._store_club(club)

    async def remove_club(self, chat_id: int):
        """
        Removes a club from the chat registry based on its chat_id.

        Args:
            chat_id (int): The chat_id of the club to be removed.
        """
        for club in self.clubs:
            if club.get_chat_id() == chat_id:
                self.clubs.remove(club)
                break

        self._delete_club(chat_id)
        await self.send_message(
            chat_id=chat_id, text=f"The club with id #{chat_id} has been removed"
        )

    async def add_team(self, team: Team, chat_id: int):
        """
        Adds a new team to the registry.

        Args:
            team (Team): The Team object to be added.
        """
        team_topic_id = team.get_team_message_thread_id()
        team_name = team.get_team_name()
        team_id = team.get_team_id()

        club = self._get_club_by_chat_id(chat_id)

        if self._is_new_chat_id(chat_id):
            await self.send_message(
                chat_id=chat_id,
                message_thread_id=team_topic_id,
                text=f"The club with id #{chat_id} does not exist, please register it first by using /start command",
                self_destruct=10,
            )
            return
        if club.has_team(team_id):
            await self.send_message(
                chat_id=chat_id,
                message_thread_id=team_topic_id,
                text=f"The team {team_name} with id #{team_id} already exists in club {club.get_title()} with id #{chat_id}",
                self_destruct=10,
            )
            return

        club.add_team(team)
        await self.send_message(
            chat_id=chat_id,
            message_thread_id=team_topic_id,
            text=f"The team {team_name} with id #{team_id} has been registered in club {club.get_title()}",
        )
        # TODO: or maybe dump to the file whore club data?
        self._store_team(team)

    async def remove_team(self, chat_id: int, message_thread_id: int, team_id: int):
        """
        Removes a team from the chat registry based on its chat_id and team_id.

        Args:
            chat_id (int): The chat_id of the club.
            team_id (int): The team identifier to be removed.
            message_thread_id (int): The team topic identifier.
        """
        if self._is_new_chat_id(chat_id):
            await self.send_message(
                chat_id=chat_id,
                message_thread_id=message_thread_id,
                text=f"The club with id #{chat_id} does not exist",
                self_destruct=10,
            )
            return
        club = self._get_club_by_chat_id(chat_id)

        team = club.get_team_by_id(team_id)

        if not team:
            await self.send_message(
                chat_id=chat_id,
                message_thread_id=message_thread_id,
                text=f"The team with id #{team_id} does not exist in club #{chat_id}",
                self_destruct=10,
            )
            return

        club.remove_team(team)
        self._delete_team(chat_id, team_id)

        await self.send_message(
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            text=f"The team {team.get_team_name()} with id #{team_id} has been removed from club {club.get_title()} #{chat_id}",
        )

    def add_app_instance(self, app: ApplicationBuilder):
        """
        Adds an application instance (bot, job_queue) to the chat registry.

        Args:
            app (ApplicationBuilder): The ApplicationBuilder instance containing the bot and job queue.
        """
        self.bot: BT = app.bot
        self.job_queue: JobQueue = app.job_queue

    # TODO move inside club
    async def run_polling(self, chat_id: int):
        """
        Start polling for a specific club identified by its chat_id.

        Args:
            chat_id (int): The chat_id of the club to start polling for.
        """
        club: Club = self._get_club_by_chat_id(chat_id)

        # If the club is not found, send an error message
        if not club:
            await self.send_message(
                chat_id=chat_id, text=f"Wrong club id #{chat_id}", self_destruct=10
            )
            return

        # Send a message about the found club
        await self.send_message(
            chat_id=chat_id,
            text=f"Club {club.get_title()} with id #{chat_id} has been found. Polling has started.",
            self_destruct=10,
        )

        # Start regular operations for the club
        job: Job = self.job_queue.run_repeating(
            self.scheduled_operation,
            interval=60,
            first=0.0,
            chat_id=chat_id,
            user_id=self.job_idx,
        )

        if job:
            self.job_idx += 1
            self.jobs.append(job)

        # TODO I guess polling for teams should be started separetly

    async def stop_polling(self, chat_id: int):
        """
        Stops polling for the specified club.

        Args:
            chat_id (int): The chat_id of the club to stop polling for.
        """
        club: Club = self._get_club_by_chat_id(chat_id)
        if not club:
            await self.send_message(
                chat_id=chat_id, text=f"Wrong club id #{chat_id}", self_destruct=10
            )
            return

        for job in self.jobs:
            job.schedule_removal()
        self.job_idx = 1

        # TODO stop polling for Teams

    # Template
    async def scheduled_operation(self, context: CallbackContext):
        """
        Executes a scheduled operation.

        Args:
            context (CallbackContext): The context passed by the job queue.
        """
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_text = f"Regular message from job #{context._user_id} in club #{context._chat_id}. Current time: {current_time}"
        await self.send_message(
            chat_id=context._chat_id, text=message_text, self_destruct=75
        )

    # TODO It seems to me that working with messages can be abstracted into a separate entity.
    async def delete_message_delayed(self, chat_id: int, message_id: int, delay: int):
        """
        Deletes a message after a specified delay.

        Args:
            chat_id (int): The ID of the chat where the message is located.
            message_id (int): The ID of the message to be deleted.
            delay (int): The delay in seconds before deleting the message.
        """
        await asyncio.sleep(delay)
        await self.bot.delete_message(chat_id=chat_id, message_id=message_id)

    async def send_message(
        self,
        chat_id: int,
        text: str,
        self_destruct: int = 0,
        message_thread_id: int = None,
    ) -> None:
        """
        Sends a message to a specified chat and schedules its deletion after a delay.

        Args:
            chat_id (int): The ID of the chat where the message will be sent.
            text (str): The text of the message.
            self_destruct (int, optional): Delay in seconds before the message is deleted. Defaults to 0.
        """

        message: Message = await self.bot.send_message(
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            text=f"{text} {'⏰' if self_destruct != 0 else ''}",
        )
        if self_destruct != 0:
            asyncio.create_task(
                self.delete_message_delayed(
                    chat_id=chat_id, message_id=message.message_id, delay=self_destruct
                )
            )

    ############################## private methods ##############################

    def _is_new_chat_id(self, chat_id: int) -> bool:
        """
        Checks if the given chat_id is new (not already registered).

        Args:
            chat_id (int): The chat_id to check.

        Returns:
            bool: True if the chat_id is new, False otherwise.
        """
        return chat_id not in [club.get_chat_id() for club in self.clubs]

    def _delete_club(self, chat_id: int) -> None:
        """
        Deletes the file associated with the given chat_id from the registry folder.

        Args:
            chat_id (int): The chat_id of the club whose file is to be deleted.
        """
        file_name = str(chat_id)
        file_path = os.path.join(self.registry_folder, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)

    def _store_club(self, club: Club) -> None:
        """
        Stores club data in a file.

        Args:
            club (Club): The club to be stored.
        """
        file_name = str(club.get_chat_id())
        file_path = os.path.join(self.registry_folder, file_name)
        if not os.path.exists(file_path):
            club_data = club.data_to_json()
            with open(file_path, "w") as file:
                json.dump(club_data, file)

    def _store_team(self, team: Team) -> None:
        """
        Adds team data to the club storage file.

        Args:
            team (Team): The team to be stored.
        """
        file_name = str(team.get_club_id())
        file_path = os.path.join(self.registry_folder, file_name)
        if os.path.exists(file_path):
            team_data = team.data_to_json()

            with open(file_path, "r") as file:
                data = json.load(file)
                if "teams" in data:
                    data["teams"].append(team_data)
                else:
                    data["teams"] = [team_data]

            with open(file_path, "w") as file:
                json.dump(data, file)

    def _delete_team(self, chat_id: int, team_id) -> bool:
        """
        Deletes the file associated with the given chat_id from the registry folder.

        Args:
            chat_id (int): The chat_id of the club whose file is to be deleted.
        """
        file_name = str(chat_id)
        file_path = os.path.join(self.registry_folder, file_name)
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                data = json.load(file)

            # Assuming 'teams' is a list of teams in the file
            if "teams" in data:
                # Filter out the team with the matching team_id
                data["teams"] = [
                    team for team in data["teams"] if team.get("team_id") != team_id
                ]

                with open(file_path, "w") as file:
                    json.dump(data, file, indent=4)
                    return True
        return False

    def _registry_restoration(self) -> None:
        """
        Performs restoration of the registry.
        """
        # TODO: Implement registry restoration logic

    def _get_club_by_chat_id(self, chat_id: int) -> Club:
        """
        Retrieves a club object based on its chat_id.

        Args:
            chat_id (int): The chat_id of the club to retrieve.

        Returns:
            Club: The club object with the specified chat_id, or None if not found.
        """
        for club in self.clubs:
            if club.get_chat_id() == chat_id:
                return club
        return None
