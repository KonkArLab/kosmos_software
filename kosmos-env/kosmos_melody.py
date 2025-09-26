from gpiozero.tones import Tone
import time

"""Définition des musique correspondant à chaque état de fonctionnement du KOSMOS"""
"""structure des mélodies : [[liste d'enchainement de notes][liste du rythme correspondant (une valeur par note)], vitesse de jeu, rapidité de la note (0 à 1)]"""
STARTING_MELODY = [["C6", "D6", "E6", "F6", "G6", "A6", "B6", "C7", "C6", "D6", "E6", "F6", "G6", "A6", "B6", "C7"],[4, 4, 4, 4, 4, 4, 4, 32, 4, 4, 4, 4, 4, 4, 4, 32], 0.015, 0.9]
STANDBY_MELODY = [["G6", "E6", "E6", "D6", "E6", "G6"],[8, 8, 16, 8, 8, 8], 0.02, 0.7]
WORKING_MELODY = [["E6", "G6", "A6", "A6", "A6", "B6", "C7", "C7", "C7", "D7", "B6", "B6", "A6", "G6", "G6", "A6"], [8, 8, 16, 16, 8, 8, 16, 16, 8, 8, 16, 16, 8, 8, 8, 16], 0.022, 0.7]
STOPPING_MELODY = [["C7", "G6", "E6", "C6"], [4, 4, 4, 8], 0.03, 0.5]
SHUTDOWN_MELODY = [["C7", "B6", "A6", "G6", "F6", "E6", "D6", "C6"], [4, 4, 4, 4, 4, 4, 4, 16], 0.03, 1]

def playMelody(buzzer, MELODY):
    speed = MELODY[2]
    note_duration = MELODY[3]
    for i in range(0, len(MELODY[0])):
        buzzer.play(Tone(note = MELODY[0][i]))
        time.sleep(MELODY[1][i]*speed*note_duration)
        buzzer.stop()
        time.sleep(MELODY[1][i]*speed*(1 - note_duration))
        buzzer.stop()
  
