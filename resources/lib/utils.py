# -*- coding: utf-8 -*-
'''

    Copyright (C) 2016 anxdpanic

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import re
import YDStreamExtractor
from YDStreamUtils import getDownloadPath
from yd_private_libs import servicecontrol
from addon_lib import log_utils
from addon_lib import kodi


get_download_path = getDownloadPath


def log_version():
    log_utils.log('Version: |%s|' % kodi.get_version())


def download_video(video_id, background=True):
    url = 'http://www.youtube.com/v/%s' % video_id
    info = YDStreamExtractor.getVideoInfo(url, quality=1)
    info = YDStreamExtractor._convertInfo(info)
    download_path = get_download_path(use_default=True)
    log_utils.log('Downloading video_id: |%s| Background: |%s|' % (video_id, str(background)))
    log_utils.log('Download Path: |%s|' % download_path)
    if background:
        servicecontrol.ServiceControl().download(info, path=download_path, duration=None)
    else:
        result = YDStreamExtractor._handleDownload(info, path=download_path, bg=False)
        if result:
            log_utils.log('Download complete: |%s| Path: |%s|' % (video_id, result.filepath))
        elif result.status != 'canceled':
            log_utils.log('Download failed: |%s| Error: |%s|' % (video_id, result.message), log_utils.LOGERROR)
            kodi.notify(msg=result.message, sound=True)
        else:
            log_utils.log('Download cancelled')


def video_id_from_plugin_url(plugin_url):
    result = re.search('video_id=(?P<video_id>.+?)(?:&|$)', plugin_url)
    if result:
        log_utils.log('Found video_id: |%s|' % result.group('video_id'))
        return result.group('video_id')
    else:
        log_utils.log('video_id not found', log_utils.LOGERROR)
        return None


def download(download_type='video', background=True):
    download_type = download_type.lower()
    plugin_url = kodi.getInfoLabel('ListItem.FileNameAndPath')
    log_utils.log('ListItem.FileNameAndPath: |%s|' % plugin_url)
    if not plugin_url:
        log_utils.log('Plugin URL not found', log_utils.LOGERROR)
        kodi.notify(msg=kodi.i18n('not_found_plugin_url'), sound=False)
        return
    video_id = video_id_from_plugin_url(plugin_url)
    if video_id:
        if download_type == 'video':
            kodi.notify(msg=kodi.i18n('download_starting'), sound=False)
            download_video(video_id, background=background)
        else:
            log_utils.log('Requested unknown download_type', log_utils.LOGERROR)
    else:
        kodi.notify(msg=kodi.i18n('not_found_video_id'), sound=False)
