from enum import Enum
from gpiozero.tones import Tone
import time

class KMelody(list, Enum):
	"""Définition des musique correspondant à chaque état de fonctionnement du KOSMOS"""
	"""structure des mélodies : [[liste d'enchainement de notes][liste du rythme correspondant (une valeur par note)], vitesse de jeu, rapidité de la note (0 à 1)]"""
	STARTING_MELODY = [["C7", "D7", "E7", "F7", "G7", "A7", "B7", "C8", "C7", "D7", "E7", "F7", "G7", "A7", "B7", "C8"],[4, 4, 4, 4, 4, 4, 4, 32, 4, 4, 4, 4, 4, 4, 4, 32], 0.01, 0.9]
	STANDBY_MELODY = [["G7", "E7", "E7", "D7", "E7", "G7"],[8, 8, 16, 8, 8, 8], 0.015, 0.7]
	WORKING_MELODY = [["E7", "G7", "A7", "A7", "A7", "B7", "C8", "C8", "C8", "D8", "B7", "B7", "A7", "G7", "G7", "A7"], [8, 8, 16, 16, 8, 8, 16, 16, 8, 8, 16, 16, 8, 8, 8, 16], 0.018, 0.7]
	STOPPING_MELODY = [["C8", "G7", "E7", "C7"], [4, 4, 4, 8], 0.02, 0.5]
	SHUTDOWN_MELODY = [["C8", "B7", "A7", "G7", "F7", "E7", "D7", "C7"], [4, 4, 4, 4, 4, 4, 4, 16], 0.02, 1]
	
	def playMelody(buzzer, MELODY):
		for i in range(0, len(MELODY[0])):
			speed = MELODY[2]
			note_duration = MELODY[3]
			buzzer.play(Tone(note = MELODY[0][i]))
			time.sleep(MELODY[1][i]*speed*note_duration)
			buzzer.stop()
			time.sleep(MELODY[1][i]*speed*(1 - note_duration))
			buzzer.stop()
