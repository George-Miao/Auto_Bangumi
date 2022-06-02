import re
import logging
from env import EnvInfo
import qbittorrentapi
import json
import os

logger = logging.getLogger(__name__)


class SetRule:
    def __init__(self):
        with open(EnvInfo.info_path, encoding="utf-8") as f:
            self.info = json.load(f)
            self.bangumi_info = self.info["bangumi_info"]
        self.rss_link = EnvInfo.rss_link
        self.host_ip = EnvInfo.host_ip
        self.user_name = EnvInfo.user_name
        self.password = EnvInfo.password
        self.download_path = EnvInfo.download_path
        self.qb = qbittorrentapi.Client(
            host=self.host_ip, username=self.user_name, password=self.password)
        try:
            self.qb.auth_log_in()
        except qbittorrentapi.LoginFailed as e:
            logger.exception(e)

    def set_rule(self, bangumi_name, group, season):
        rule = {
            'enable': True,
            'mustContain': bangumi_name,
            'mustNotContain': EnvInfo.not_contain,
            'useRegx': True,
            'episodeFilter': '',
            'smartFilter': False,
            'previouslyMatchedEpisodes': [],
            'affectedFeeds': [self.rss_link],
            'ignoreDays': 0,
            'lastMatch': '',
            'addPaused': False,
            'assignedCategory': 'Bangumi',
            'savePath': str(os.path.join(EnvInfo.download_path, re.sub(EnvInfo.rule_name_re, " ", bangumi_name).strip(), season))
        }
        if EnvInfo.enable_group_tag:
            rule_name = f"[{group}] {bangumi_name}"
        else:
            rule_name = bangumi_name
        self.qb.rss_set_rule(rule_name=rule_name, rule_def=rule)

    def rss_feed(self):
        try:
            self.qb.rss_remove_item(item_path="Mikan_RSS")
        except qbittorrentapi.exceptions.Conflict409Error:
            logger.debug("No feed exists, starting adding feed.")
        try:
            self.qb.rss_add_feed(url=self.rss_link, item_path="Mikan_RSS")
            logger.debug("Successes adding RSS Feed.")
        except ConnectionError:
            logger.debug("Error with adding RSS Feed.")
        except qbittorrentapi.exceptions.Conflict409Error:
            logger.debug("RSS Already exists.")

    def run(self):
        logger.debug("Start adding rules.")
        for info in self.bangumi_info:
            if not info["added"]:
                self.set_rule(info["title"], info["group"], info["season"])
                info["added"] = True
        with open(EnvInfo.info_path, 'w', encoding='utf8') as f:
            json.dump(self.info, f, indent=4, separators=(
                ',', ': '), ensure_ascii=False)
        logger.debug("Finished.")


if __name__ == "__main__":
    put = SetRule()
    put.run()
