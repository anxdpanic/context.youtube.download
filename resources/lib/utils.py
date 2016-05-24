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
import sys
import urllib
import YDStreamExtractor
from addon_lib import log_utils
from addon_lib import kodi


YOUTUBE_DL_SCRIPT_ID = 'script.module.youtube.dl'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20150101 Firefox/44.0 (Chrome)'


def youtube_dl_control():
    script_path = 'special://home/addons/%s/control.py' % YOUTUBE_DL_SCRIPT_ID
    kodi.execute_builtin('RunScript(%s)' % script_path)


def youtube_dl_settings():
    kodi.Addon(YOUTUBE_DL_SCRIPT_ID).openSettings()


def log_version():
    log_utils.log('Version: |%s|' % kodi.get_version())


def _download(video_id, info, background=True):
    if background:
        YDStreamExtractor.handleDownload(info, bg=background)
    else:
        result = YDStreamExtractor.handleDownload(info, bg=background)
        if result:
            log_utils.log('Download complete: |%s| Path: |%s|' % (video_id, result.filepath))
        elif result.status != 'canceled':
            log_utils.log('Download failed: |%s| Error: |%s|' % (video_id, result.message), log_utils.LOGERROR)
            kodi.notify(msg=result.message, sound=True)
        else:
            log_utils.log('Download cancelled')


def get_video_info(url):
    info = YDStreamExtractor.getVideoInfo(url)
    if hasattr(info, '_streams'):
        return info
    else:
        log_utils.log('Stream not available: |%s|' % url, log_utils.LOGERROR)
        kodi.notify(msg=kodi.i18n('stream_not_available'), sound=False)
        return None


def download_video(video_id, background=True):
    url = 'http://www.youtube.com/v/%s' % video_id
    info = get_video_info(url)
    if info:
        log_utils.log('Downloading: |video| video_id: |%s| Background: |%s|' % (video_id, str(background)))
        _download(video_id, info, background)


def download_audio(video_id, background=True):
    url = 'http://www.youtube.com/v/%s' % video_id
    info = get_video_info(url)
    if info:
        stream = info._streams[0]
        ytdl_format = stream.get('ytdl_format', {})
        formats = ytdl_format.get('formats', [])
        best_quality = 0
        best_format = None
        if formats:
            for fmt in formats:
                fmt_desc = fmt.get('format', '')
                if 'audio only' in fmt_desc.lower():
                    ext = fmt.get('ext')
                    if ext == 'm4a':
                        tbr = int(fmt.get('tbr'))
                        if tbr > best_quality:
                            best_quality = tbr
                            best_format = fmt
            if best_format:
                stream['xbmc_url'] = best_format['url'] + '|' + urllib.urlencode({'User-Agent': USER_AGENT})
                stream['url'] = best_format['url']
                stream['ytdl_format'].update(best_format)
                stream['ytdl_format']['formats'] = [best_format]
                info._streams = [stream]
                log_utils.log('Downloading: |audio| video_id: |%s| Background: |%s|' % (video_id, str(background)))
                _download(video_id, info, background)
            else:
                log_utils.log('No audio-only stream formats found: |%s|' % video_id, log_utils.LOGERROR)
                kodi.notify(msg=kodi.i18n('no_audio_stream_formats'), sound=False)
        else:
            log_utils.log('No stream formats found: |%s|' % video_id, log_utils.LOGERROR)
            kodi.notify(msg=kodi.i18n('no_stream_formats'), sound=False)


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
    plugin_url = sys.listitem.getfilename()
    log_utils.log('ListItem.FileNameAndPath: |%s|' % plugin_url)
    if not plugin_url:
        log_utils.log('Plugin URL not found', log_utils.LOGERROR)
        kodi.notify(msg=kodi.i18n('not_found_plugin_url'), sound=False)
        return
    video_id = video_id_from_plugin_url(plugin_url)
    if video_id:
        if download_type == 'video':
            download_video(video_id, background=background)
        elif download_type == 'audio':
            download_audio(video_id, background=background)
        else:
            log_utils.log('Requested unknown download_type: |%s|' % download_type, log_utils.LOGERROR)
    else:
        kodi.notify(msg=kodi.i18n('not_found_video_id'), sound=False)
