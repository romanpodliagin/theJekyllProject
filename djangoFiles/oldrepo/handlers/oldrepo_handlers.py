import os
import re
import subprocess

from django.conf import settings

from jeklog.handlers.page_handler import PageHandler
from jeklog.handlers.post_handler import PostHandler

from oldrepo.constants import (
    EARLY_CHECK_FAILS, FILES_NOT_FOUND, OLD_REPO_SUCCESS
)

from theJekyllProject.dbio import (
    RepoDbIO, SiteDataDbIO, SiteExcludeDbIO, SitePluginDbIO,
    SiteSocialProfileDbIO, SiteThemeDbIO
)


class OldRepoSetUp:
    def __init__(self, user, repo_name):
        self.user = user
        self.repo_name = repo_name
        self.base_dir = settings.BASE_DIR
        self.user_path = '/'.join([self.base_dir, '..', 'JekLog',
                                   self.user.username])
        self.repo_path = '/'.join([self.base_dir, '..', 'JekLog',
                                   self.user.username, self.repo_name])

    # FIXME YOU CAN"T CALL static methods in the same class.
    # Copied functions to theJekyllProject/handlers/scrape_files.py
    @staticmethod
    def find_in_content(regex, file_data):
        """
        Find something in the content and return things accordingly
        """
        data_found = re.findall(regex, file_data)
        return data_found[0].split(':')[1].strip()

    @staticmethod
    def find_multi_line_content(regex, file_data):
        """
        find and return multi line values in file_data with regex

        expected input:
            regex = exclude:

            file_data = {
                name: something
                code: something
                exclude:
                    - Real-job
                    - README
            }
        expected output:
            ['Real-job', 'README']
        """
        return_list = []
        file_data = file_data.split('\n')
        iterator = iter(file_data)
        line = next(iterator)

        # Try to find regex in the line
        while True:
            if re.search(regex, line):
                break
            else:
                line = next(iterator)

        # When you find it find  and return the list of options
        while True:
            line = next(iterator).strip()
            if line[:1] is '-':
                return_list.append(line.split(' ')[1])
            else:
                break
        return return_list

    def early_checks(self):
        """
        Make some earlier checks about the code.
        Directly return True for now.
        """
        return True

    def git_clone_repo(self):
        """git_clone_repo to clone the already created Repository and store at
        a particular location.

        Example:
            Triggers when:
            User clicks on one of the already created repository
            clamining that the repo contains the required files.

        Tasks:
            * Works for a logged in user
            * clone the repository to particular path
        """
        url = '/'.join(['https://github.com', self.user.username,
                        self.repo_name])
        subprocess.call(['git', 'clone', url, self.repo_path])

    def find_required_files(self):
        """find_required_files to find particular files in the cloned repo.
        We try to find _config.yml file and _posts directory. If we find both
        of them it returns success
        """
        files = os.listdir(self.repo_path)
        temp = 0
        for file in files:
            if(file == '_config.yml'):
                temp = temp + 1
            elif(file == '_posts'):
                temp = temp + 1
        if(temp == 2):
            return True
        else:
            return False

    def store_old_repo(self):
        """store_old_repo to fill the repo table for choosen
        old repo
        """
        data = {
            'user': self.user,
            'repo': self.repo_name,
            'main': True
        }
        return RepoDbIO().create_return(data)

    def read_config_data(self):
        """read_config_data to read config file and return data
        """
        config_file_path = '/'.join([self.repo_path, '_config.yml'])
        with open(config_file_path, 'r') as config_file:
            file_data = config_file.read()

        return_data = {}
        rdsd = return_data['site_data'] = {}
        rdssd = return_data['social_site_data'] = {}
        rdst = return_data['site_theme'] = {}
        rdse = return_data['site_exclude'] = {}
        rdsp = return_data['site_plugin'] = {}
        # Find SiteData
        rdsd['title'] = self.find_in_content(r'name:.+', file_data)
        rdsd['description'] = self.find_in_content(r'description:.+',
                                                   file_data)
        rdsd['avatar'] = self.find_in_content(r'avatar:.+', file_data)

        # Find SocialSiteData
        rdssd['dribbble'] = self.find_in_content(r'dribbble:.+|dribbble:',
                                                 file_data)
        rdssd['email'] = self.find_in_content(r'email:.+|email:', file_data)
        rdssd['facebook'] = self.find_in_content(r'facebook:.+|facebook:',
                                                 file_data)
        rdssd['flickr'] = self.find_in_content(r'flickr:.+|flickr:', file_data)
        rdssd['github'] = self.find_in_content(r'github:.+|github:', file_data)
        rdssd['instagram'] = self.find_in_content((r'instagram:.+|inst'
                                                   r'agram:'), file_data)
        rdssd['linkedin'] = self.find_in_content(r'linkedin:.+|linkedin:',
                                                 file_data)
        rdssd['pinterest'] = self.find_in_content((r'pinterest:.+|pin'
                                                   r'terest:'), file_data)
        rdssd['rss'] = self.find_in_content(r'rss:.+|rss:', file_data)
        rdssd['twitter'] = self.find_in_content(r'twitter:.+|twitter:',
                                                file_data)
        rdssd['stackoverflow'] = self.find_in_content((r'stackoverflow:.+'
                                                       r'|stackoverflow:'),
                                                      file_data)
        rdssd['youtube'] = self.find_in_content(r'youtube:.+|youtube:',
                                                file_data)
        rdssd['googleplus'] = self.find_in_content((r'googleplus:.+|googl'
                                                    r'eplus:'), file_data)
        rdssd['disqus'] = self.find_in_content(r'disqus:.+|disqus:', file_data)
        rdssd['google_analytics'] = self.find_in_content((r'google_analyt'
                                                          r'ics:.+|google'
                                                          r'_analytics:'),
                                                         file_data)

        # Find theme data
        rdst['theme'] = self.find_in_content(r'theme:.+|theme:', file_data)

        # Find the exclude data
        rdse['exclude'] = self.find_multi_line_content(r'exclude:', file_data)
        # Find the plugin/gems data
        rdsp['plugin'] = self.find_multi_line_content(r'gems:', file_data)
        return return_data

    def store_config_data(self, repo):
        """store_config_data to fill the database for choosen
        old repo:
            * Store SiteData
            * Store SiteSocialData
            * Store SiteTheme
            * Store SitePlugins
            * Store SiteExcludes
        """
        RepoDbIO().change_main(self.user, repo)
        config_data = self.read_config_data()
        config_data['site_data'].update({'repo': repo})
        config_data['social_site_data'].update({'repo': repo})
        config_data['site_theme'].update({'repo': repo})
        config_data['site_plugin'].update({'repo': repo})
        config_data['site_exclude'].update({'repo': repo})
        SiteDataDbIO().save_db_instance(config_data['site_data'])
        SiteSocialProfileDbIO().save_db_instance(
                config_data['social_site_data'])
        SiteThemeDbIO().save_db_instance(config_data['site_theme'])
        SitePluginDbIO().save_db_instance(config_data['site_plugin'])
        SiteExcludeDbIO().save_db_instance(config_data['site_exclude'])

    def use_old_repo(self):
        """
        Tasks:
        * View for logged in users only.
        * Select any repo from the repo list
        * Make some earlier checks
        * Clone the repo
        * Check if the required contents are present or not
        * If yes do the required operations:
            * Fill repo table
            * Select Main Site
        * Else give an error message
        * Integrate celery to show the amount of task completed
        """
        self.git_clone_repo()
        return_dict = {}
        if not self.early_checks():
            # FIXME take the user to same url with error as message
            return_dict['message'] = EARLY_CHECK_FAILS
            return_dict['message_type'] = 'error'
            return return_dict

        if not self.find_required_files():
            # FIXME same case must be followed here
            return_dict['messages'] = FILES_NOT_FOUND
            return_dict['message_type'] = 'error'
            return return_dict

        else:
            repo = self.store_old_repo()
            self.store_config_data(repo)
            PostHandler(self.user, self.repo_name).read_posts()
            PageHandler(self.user, self.repo_name).read_pages()
            return_dict['message'] = OLD_REPO_SUCCESS
            return_dict['message_type'] = 'success'
            return return_dict
