from queue import Queue
import pygame
import numpy as np
import time


class GroundStation:
    def __init__(self, x, y, totUAV):
        self.x = x  # fixed position
        self.y = y
        self.busy = False  # per i pacchetti. Nota: per ora non consideriamo il queueing delay
        self.buffer = Queue()

        self.SF_w = 500
        self.SF_h = 154

        self.flag_missing = 0
        self.drone_found_miss_id = -1

        self.priority = 0
        self.type = None
        self.arrival_time = 0
        self.gen_time = 0
        self.time_found = 0
        self.queue_owner = None
        self.queue_owner_ID = 0
        self.pkt_owner = 0

        self.pkts_UAV = np.zeros((2, totUAV + 1))

    def receive(self):

        if not self.busy and not self.buffer.empty():
            self.busy = True
            packet = self.buffer.get()
            (self.arrival_time, self.gen_time, self.queue_owner, self.pkt_owner, self.priority, self.type,
             cnt_packet_sent, total_pkt) = packet
            if self.queue_owner == 'relay':
                self.queue_owner_ID = 0
            else:
                self.queue_owner_ID = self.pkt_owner

            if self.priority == 1:
                self.flag_missing = 1
                self.drone_found_miss_id = self.pkt_owner
                self.time_found = self.arrival_time
           #     print('GS: ive received a pkt:\n -time: ', self.time, '\n -type: ', self.type, '\n -ID', self.UAVid, '\n -priority: ', self.priority, '\n -cnt_pkt: ', cnt_packet_sent, '\n')
                #time.sleep(.5)  # simulate processing time
            id_drone = self.queue_owner_ID
            self.pkts_UAV[0, id_drone] = cnt_packet_sent
            self.pkts_UAV[1, id_drone] = total_pkt
            # self.pkts_UAV[2, id_drone - 1] = self.priority
            self.busy = False
          #  print('GS: Processed packet from: ', self.UAVid, 'at time: ', self.time)
        #elif self.busy and not self.buffer.empty():
           # print(f'GS: Received packet from: ', id_drone, 'at time: ', sim_time)

    def pc_controller(self, screen, estimated_position, width):
        font = pygame.font.Font('cour.ttf', 18)
        font.set_bold(True)
        # font = pygame.font.SysFont(font, 25)

        # Aggiungi la scritta alla superficie SF_display
        min = np.floor(self.arrival_time / 60)
        sec = np.floor(self.arrival_time % 60)
        cent = (self.arrival_time - (min * 60 + sec))

        min_found = np.floor(self.time_found / 60)
        sec_found = np.floor(self.time_found % 60)
        cent_found = (self.time_found - (min_found * 60 + sec_found))

       # print('queue_owner_ID: ', self.queue_owner_ID)
        if self.pkts_UAV[1, self.queue_owner_ID] != 0:
            percentage = (100 * self.pkts_UAV[0, self.queue_owner_ID] / self.pkts_UAV[1, self.queue_owner_ID])
        else:
            percentage = 100
        text1 = font.render('Telemetry of UAVid: %d send by: %s' % (self.pkt_owner, self.queue_owner), True, pygame.Color('white'))
        text2 = font.render('Received at time: %d [min] %d.%d [s]' % (min, sec, cent), True, pygame.Color('white'))
        text4 = font.render('The missing is found by UAVid: %d at: %d [min] %d.%d [s]' % (self.drone_found_miss_id, min_found, sec_found, cent_found), True, pygame.Color('white'))
        text3 = font.render('Data Type: %s LOADING FILE: %.2f %% ' %(self.type,percentage), True, pygame.Color('white'))

        text5 = font.render('Coordinate: (%.2f, %.2f) [m]' % (estimated_position[0], estimated_position[1])
                            , True, pygame.Color('white'))

        text6 = font.render('The buffer of gs is full ', True, pygame.Color('white'))

        text0 = font.render('None missing is found yet ', True, pygame.Color('white'))




        # Imposta la dimensione della superficie SF_display
        self.SF_w = width
        self.SF_h = 100

        # Crea la superficie di SF_display
        SF_display = pygame.Surface((self.SF_w, self.SF_h), pygame.SRCALPHA)  # per-pixel alpha

        # Disegna il rettangolo azzurro sulla superficie di SF_display
        SF_display.fill(pygame.Color('blue'))

        # Disegna la cornice grigia attorno al rettangolo azzurro
        border_rect = pygame.Rect(0, 0, self.SF_w, self.SF_h)
        pygame.draw.rect(SF_display, [255, 165, 0], border_rect, 7)

        # Aggiungi le scritte alla superficie SF_display con la spaziatura richiesta
        text_x, text_y = 10, 10

        SF_display.blit(text1, (text_x, text_y))
        text_y += text1.get_height() + 5
        SF_display.blit(text2, (text_x, text_y))
        text_y += text2.get_height() + 5
        SF_display.blit(text3, (text_x, text_y))
        text_y += text3.get_height() + 9

        Text_width = text0.get_width()
        text_x = width/2 - Text_width/2
        text_y = 10
        if self.flag_missing == 0:
            SF_display.blit(text0, (text_x, text_y))
            text_y += text0.get_height() + 5
        else:
            # priority == 1
            # missing person found #
            SF_display.blit(text4, (text_x, text_y))
            text_y += text4.get_height() + 5
            SF_display.blit(text5, (text_x, text_y))
            text_y += text5.get_height() + 5


        if self.buffer.full():
            SF_display.blit(text6, (text_x, text_y))

        # Disegna la superficie di SF_display sulla finestra di gioco
        screen.blit(SF_display, (0, 0))

    #    print('GS: ive received a pkt:\n -time: ', self.time, '\n -type: ', self.type, '\n -ID', self.drone_found_miss_id,
     #         '\n -priority: ', self.priority, '\n')
