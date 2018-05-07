"""
Python wrapper for ffprobe command line tool.
First it will check whether ffprobe command is available or not and then
for given file, it will extract the streams and frames information.
"""
import os
import pipes
import platform
import json
import subprocess

__author__     = 'Parth Shah'
__version__    = '0.1'
__email__      = "contactparthshah@gmail.com"

class FFProbe:
    '''
    FFProbe wraps the ffprobe command and pulls the data into an object form:
    obj=FFProbe('1.mov')
    '''
    def __init__(self, movie_file,ffprobe_bin='ffprobe',frame_info=1,log_debug=0):
        '''
        Constructor of Class
        '''
        self._init_all_vars()

        self.movie_file = movie_file
        self.ffprobe_bin = ffprobe_bin
        self.frame_info = frame_info
        self.log_debug = log_debug

        try:
            with open(os.devnull, 'w') as tempf:
                subprocess.check_call([self.ffprobe_bin, "-h"], stdout=tempf, stderr=tempf)
        except:
            raise IOError('ffprobe not found.')

        if os.path.isfile(self.movie_file):
            ###Extracting Stream Details
            self._extract_stream_details()

            ###Extracting Format Details
            self._extract_format_details()

            if self.frame_info:
                ###Extracting Frame Details
                self._extract_frame_details()
        else:
            raise IOError('No such media file ' + self.movie_file)

    def _init_all_vars(self):
        '''
            Initialize all global variables in one place
        '''
        self.movie_file = None
        self.ffprobe_bin = None
        self.frame_info = None
        self.log_debug = None
        self.format_details = {}
        self.video = {}
        self.audio = {}
        self.data = {}
        self.subtitle = {}
        self.frames = {}

    def __enter__(self):
        '''
        Constructor of context manager - with
        '''
        return self

    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        '''
        Destructor of context manager - with
        '''
        self._init_all_vars()

    def _execute_cmd(self,cmd):
        '''
        Execute command and return its output
        '''
        if self.log_debug:
            print '\ncmd %s\n'%(cmd)

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        json_data = json.loads(p.stdout.read())
        p.stdout.close()
        p.stderr.close()
        p.stdout.close()
        p.stderr.close()

        if self.log_debug:
            print 'type(json_data) %s and json_data %s'%(type(json_data),json_data)

        return json_data

    def _extract_format_details(self):
        '''
        This function will extract "-show_format" stream information from file.
        Based on this self.format_details info will be available.
        '''
        cmd = [self.ffprobe_bin + "  -v quiet -print_format json -show_format " + pipes.quote(self.movie_file)]

        json_data = self._execute_cmd(cmd)
        self.format_details = json_data['format']

        if self.log_debug:
            print '\n---------\nself.format_details %s\n---------'%(self.format_details)

    def _extract_stream_details(self):
        '''
        This function will extract "-show_streams" stream information from file.
        Based on that self.audio,self.video and self.data,self.subtitle info will be available.
        '''
        cmd = [self.ffprobe_bin + "  -v quiet -print_format json -show_streams " + pipes.quote(self.movie_file)]

        json_data = self._execute_cmd(cmd)

        video_counter = 0
        audio_counter = 0
        data_counter = 0
        subtitle_counter = 0
        for single_dict in json_data['streams']:
            if single_dict['codec_type'].lower() == 'video':
                video_counter += 1
                self.video[video_counter] = {}
                self.video[video_counter] = single_dict
            elif single_dict['codec_type'].lower() == 'audio':
                audio_counter += 1
                self.audio[audio_counter] = {}
                self.audio[audio_counter] = single_dict
            elif single_dict['codec_type'].lower() == 'data':
                data_counter += 1
                self.data[data_counter] = {}
                self.data[data_counter] = single_dict
            elif single_dict['codec_type'].lower() == 'subtitle':
                subtitle_counter += 1
                self.subtitle[subtitle_counter] = {}
                self.subtitle[subtitle_counter] = single_dict
            else:
                raise Exception('Unknown "%s" codec_type found,Please add support.'%(single_dict['codec_type']))

        if self.log_debug:
            print '\n---------\nself.video %s\n---------'%(self.video)
            print '\n---------\nself.audio %s\n---------'%(self.audio)
            print '\n---------\nself.data  %s\n---------'%(self.data)
            print '\n---------\nself.subtitle  %s\n---------'%(self.subtitle)

    def _extract_frame_details(self):
        '''
        This function will extract "-show_frames" stream information from file.
        Based on that self.frames will be available.
        '''
        if str(platform.system()).lower() == 'windows':
            cmd = [self.ffprobe_bin, "-v", "quiet", "-print_format", "json", "-show_frames", self.movie_file]
        else:
            cmd = [self.ffprobe_bin + "  -v quiet -print_format json -show_frames " + pipes.quote(self.movie_file)]

        json_data = self._execute_cmd(cmd)
        video_counter = 0
        audio_counter = 0
        data_counter = 0
        subtitle_counter = 0
        counter = 0
        for single_dict in json_data['frames']:
            media_type = single_dict['media_type'].lower()
            stream_index = single_dict['stream_index']

            if not media_type in self.frames:
                self.frames[media_type] = {}
                self.frames[media_type]['overall_stream_index'] = []

            if not stream_index in self.frames[media_type]['overall_stream_index']:
                self.frames[media_type]['overall_stream_index'].append(stream_index)
                if media_type.lower() == 'video':
                    video_counter += 1
                    self.frames[media_type][video_counter] = {}
                elif media_type.lower() == 'audio':
                    audio_counter += 1
                    self.frames[media_type][audio_counter] = {}
                elif media_type.lower() == 'data':
                    data_counter += 1
                    self.frames[media_type][data_counter] = {}
                elif media_type.lower() == 'subtitle':
                    subtitle_counter += 1
                    self.frames[media_type][subtitle_counter] = {}
                else:
                    raise Exception('Unknown "%s" codec_type found,Please add support.'%(media_type.lower()))

            if media_type.lower() == 'video':
                counter = video_counter
            elif media_type.lower() == 'audio':
                counter = audio_counter
            elif media_type.lower() == 'data':
                counter = data_counter
            elif media_type.lower() == 'subtitle':
                counter = subtitle_counter
            else:
                raise Exception('Unknown "%s" codec_type found,Please add support.'%(media_type.lower()))

            for key,val in single_dict.iteritems():
                if not key in self.frames[media_type][counter]:
                    self.frames[media_type][counter][key] = []
                self.frames[media_type][counter][key].append(val)

        if self.log_debug:
            for key in self.frames:
                print '\n---------\nself.frames[%s] %s\n---------'%(key,self.frames[key])

    def isVideo(self):
        '''
        File has video or not
        '''
        if len(self.video) > 0:
            return True
        return False

    def isAudio(self):
        '''
        File has audio or not
        '''
        if len(self.audio) > 0:
            return True
        return False

    def isData(self):
        '''
        File has data or not
        '''
        if len(self.data) > 0:
            return True
        return False

    def isSubtitle(self):
        '''
        File has subtitle or not
        '''
        if len(self.subtitle) > 0:
            return True
        return False

    def get_stream_details(self,codec_type,track_number,tag):
        if codec_type.lower() == 'video':
            if track_number in self.video and tag in self.video[track_number]:
                return self.video[track_number][tag]
        elif codec_type.lower() == 'audio':
            if track_number in self.audio and tag in self.audio[track_number]:
                return self.audio[track_number][tag]
        elif codec_type.lower() == 'data':
            if track_number in self.data and tag in self.data[track_number]:
                return self.data[track_number][tag]
        elif codec_type.lower() == 'subtitle':
            if track_number in self.subtitle and tag in self.subtitle[track_number]:
                return self.subtitle[track_number][tag]
        else:
            raise Exception('Unknown "%s" codec_type found,Please add support.'%(codec_type))
        return None

    def get_frame_details(self,codec_type,track_number,tag):
        if codec_type in self.frames and track_number in self.frames[codec_type] and tag in self.frames[codec_type][track_number]:
            return self.frames[codec_type][track_number][tag]
        return None

    def get_format_details(self,tag):
        if tag in self.format_details:
            return self.format_details[tag]
        return None
