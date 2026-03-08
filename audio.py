from pygame import mixer
from classes import Music

mixer.pre_init(44100, -16, 2, 50)

folder = "assets/audio/slowdown/tracksOGG/"

intro = [folder + "0_intro.ogg", folder + "1_buildup.ogg", folder + "2_transitiondrop.ogg"]
body = [folder + "3_main.ogg", folder + "3_main.ogg" folder + "4_break.ogg"]
outro = [folder + "5_slow.ogg", folder + "6_outro.ogg"]

song = [intro, body, outro]



def AudioManager(state, nextState, currentTrack, previousTrack, songTime):
    mixer.music.set_volume(1)

    if previousTrack == -1:
        print(f"Play track {state, currentTrack}")

        mixer.music.load(song[state][currentTrack])

        mixer.music.play()
        
        if nextState == state:
            nextSong = currentTrack + 1
            if nextSong > len(song[state]) - 1:
                nextSong = 0
        else:
            nextSong = 0
            state = nextState

        print(f"Queud track {state, nextSong}")
        mixer.music.queue(song[state][nextSong])

        songTime = 0

        return Music(state, nextState, nextSong, currentTrack, songTime, True)
    
    previousState = state - 1
    if previousState > len(song) - 1:
        previousState = 0
    songLength = mixer.Sound(song[previousState][previousTrack]).get_length()
    
    if songTime >= songLength:

            if nextState == state:
                nextSong = currentTrack + 1
                if nextSong > len(song[state]) - 1:
                    nextSong = 0
            else:
                nextSong = 0
                state = nextState

            print(f"Queud track {state, nextSong}")
            mixer.music.queue(song[state][nextSong])

            songTime = 0

            return Music(state, nextState, nextSong, currentTrack, songTime, True)
    
    
    
    return Music(state, nextState, currentTrack, previousTrack, songTime, False)