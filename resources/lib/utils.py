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
from addon_lib import log_utils
from addon_lib import kodi


def download_video(video_id, bg=True):
    url = 'http://www.youtube.com/v/%s' % video_id
    info = YDStreamExtractor.getVideoInfo(url, quality=1)
    info = YDStreamExtractor._convertInfo(info)
    log_utils.log('Downloading video_id: |%s|' % video_id)
    result = YDStreamExtractor._handleDownload(info, bg=bg)
    if result:
        log_utils.log('Download complete: |%s| Path: |%s|' % (video_id, result.filepath))
    elif result.status != 'canceled':
        log_utils.log('Download failed: |%s| Error: |%s|' % (video_id, result.message), log_utils.LOGERROR)
        kodi.notify(msg=result.message, sound=True)
    else:
        log_utils.log('Download cancelled')


def get_video_id(path):
    res = re.search('video_id=(.+?)(?:&|$)', path)
    if res:
        return res.group(1)
    else:
        return None


def download(bg=True):
    log_utils.log('Version: |%s|' % kodi.get_version())
    path = kodi.getInfoLabel('ListItem.FileNameAndPath')
    log_utils.log('ListItem Path: |%s|' % path)
    if not path:
        log_utils.log('Plugin URL not found', log_utils.LOGERROR)
        kodi.notify(msg=kodi.i18n('not_found_plugin_url'), sound=False)
        return
    video_id = get_video_id(path)
    if video_id:
        download_video(video_id, bg=bg)
    else:
        log_utils.log('video_id not found', log_utils.LOGERROR)
        kodi.notify(msg=kodi.i18n('not_found_video_id'), sound=False)
