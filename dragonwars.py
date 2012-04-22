import pygame, sys, copy, random, time
from pygame.locals import *

FPS = 50
SZYBKOSC_ANIMACJI = 25

SZEROKOSC_OKNA = 800
WYSOKOSC_OKNA = 480

KOLUMNY = 8
WIERSZE = 8

JEWEL_ROZMIAR = 48

PUSTE_MIEJSCE = -1

JEWEL_ILOSC_RODZAJOW = 7

BLACK     = (  0,  0,  0, 0 )
WHITE     = (255,255,255)

KOLOR_SIATKI = WHITE 
KOLOR_WYNIKU = WHITE

MARGINES_X = int((SZEROKOSC_OKNA - (JEWEL_ROZMIAR * KOLUMNY)) / 2)
MARGINES_Y = int((WYSOKOSC_OKNA - (JEWEL_ROZMIAR * WIERSZE)) / 2)

GO = 'gora'
DO = 'dol'
LE= 'lewo'
PR = 'prawo'

WIERSZ_NAD_PLANSZA = 'xxxxx'

def main():
	global FPSZEGAR, DISPLAYSURF, JEWELS_OBRAZKI, DZWIEKI, CZCIONKA, JEWEL_RAMKI
	pygame.init()
	FPSZEGAR = pygame.time.Clock()
	DISPLAYSURF = pygame.display.set_mode((SZEROKOSC_OKNA, WYSOKOSC_OKNA))
	pygame.display.set_caption('Dragon Wars')
	CZCIONKA = pygame.font.Font('freesansbold.ttf', 24)
	JEWELS_OBRAZKI = []
	for i in range(1, JEWEL_ILOSC_RODZAJOW+1):
		jewelObrazek = pygame.image.load('gem%s.png' % i)
		JEWELS_OBRAZKI.append(jewelObrazek)
	
	DZWIEKI = {}
	DZWIEKI['zle'] = pygame.mixer.Sound('zle.wav')
	DZWIEKI['dobrze'] = pygame.mixer.Sound('dobrze.wav')
	
	JEWEL_RAMKI = []
    

	for x in range(KOLUMNY):
		JEWEL_RAMKI.append([])
		for y in range(WIERSZE):
			r = pygame.Rect((MARGINES_X + (x * JEWEL_ROZMIAR),
							 MARGINES_Y + (y * JEWEL_ROZMIAR),
							 JEWEL_ROZMIAR,
							 JEWEL_ROZMIAR))
			JEWEL_RAMKI[x].append(r)		
    

    
	while True:
		uruchomGre()

def uruchomGre():
	siatkaGry = getPustaSiatka()
	wynik = 0
	wypelnijSiatkeJewelami(siatkaGry, [], wynik)
	
	ostatnieKlikniecieX = None
	ostatnieKlikniecieY = None
	gameOver = False
	pierwszyWybranyJewel = None
	
	while True:
		if gameOver:
				nomore =  pygame.image.load('nomore.png')
				rr = pygame.Rect(0,0,800,480)
				DISPLAYSURF.blit(nomore, rr)
				pygame.display.update()
		kliknietePole = None
		for event in pygame.event.get():
			if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
				pygame.quit()
				sys.exit()
			elif event.type == KEYUP and event.key == K_BACKSPACE:
				return
			elif event.type == MOUSEBUTTONUP:
				if gameOver:
					return
				if event.pos == (ostatnieKlikniecieX, ostatnieKlikniecieY):
					kliknietePole = sprawdzCzyKliknietoJewela(event.pos)
				else:
					pierwszyWybranyJewel = sprawdzCzyKliknietoJewela((ostatnieKlikniecieX, ostatnieKlikniecieY))
					kliknietePole = sprawdzCzyKliknietoJewela(event.pos)
					if not pierwszyWybranyJewel or not kliknietePole:
						pierwszyWybranyJewel = None
						kliknietePole = None
			elif event.type == MOUSEBUTTONDOWN:
				ostatnieKlikniecieX, ostatnieKlikniecieY = event.pos
		
		if kliknietePole and not pierwszyWybranyJewel:
			pierwszyWybranyJewel = kliknietePole
		elif kliknietePole and pierwszyWybranyJewel:
			pierwszyZamienianyJewel, drugiZamienianyJewel = ustawZamienianeJewele(siatkaGry, pierwszyWybranyJewel, kliknietePole)
			if pierwszyZamienianyJewel == None and drugiZamienianyJewel == None:
				pierwszyWybranyJewel = None
				continue
			
			kopiaSiatki = getKopiaSiatkiBezNiektorychJeweli(siatkaGry, (pierwszyZamienianyJewel, drugiZamienianyJewel))
			animujJewele(kopiaSiatki, [pierwszyZamienianyJewel, drugiZamienianyJewel], [], wynik)

			siatkaGry[pierwszyZamienianyJewel['x']][pierwszyZamienianyJewel['y']] = drugiZamienianyJewel['rodzajJewela']
			siatkaGry[drugiZamienianyJewel['x']][drugiZamienianyJewel['y']] = pierwszyZamienianyJewel['rodzajJewela']
			
			pasujaceJewele = znajdzPasujaceJewele(siatkaGry)
			
			if pasujaceJewele == []:
				DZWIEKI['zle'].play()
				animujJewele(kopiaSiatki, [pierwszyZamienianyJewel, drugiZamienianyJewel], [], wynik)
				siatkaGry[pierwszyZamienianyJewel['x']][pierwszyZamienianyJewel['y']] = pierwszyZamienianyJewel['rodzajJewela']
				siatkaGry[drugiZamienianyJewel['x']][drugiZamienianyJewel['y']] = drugiZamienianyJewel['rodzajJewela']			
			else:
				dodajWynik = 0
				while pasujaceJewele != [] :
					for zbiorJeweli in pasujaceJewele:
						dodajWynik += (9 + ((len(zbiorJeweli) - 3) * 2))
						for jewel in zbiorJeweli:
							siatkaGry[jewel[0]][jewel[1]] = PUSTE_MIEJSCE
					DZWIEKI['dobrze'].play()
					
					wynik += dodajWynik
					
					wypelnijSiatkeJewelami(siatkaGry, [], wynik)
					
					pasujaceJewele = znajdzPasujaceJewele(siatkaGry)
			pierwszyWybranyJewel = None
			
			if not istniejaRuchy(siatkaGry):
				gameOver = True
				nomore =  pygame.image.load('nomore.png')
				rr = pygame.Rect(0,0,800,480)
				DISPLAYSURF.blit(nomore, rr)
				pygame.display.update()
				
		if not gameOver:	
			tlo =  pygame.image.load('tlo.png')
			rr = pygame.Rect(0,0,800,480)
			DISPLAYSURF.blit(tlo, rr)
			rysujSiatke(siatkaGry)
			rysujWynik(wynik)
			pygame.display.update()
		FPSZEGAR.tick(FPS)			


			

def znajdzPasujaceJewele(siatka):
	jeweleDoUsuniecia = []
	kopiaSiatki = copy.deepcopy(siatka)
	
	for x in range (KOLUMNY):
		for y in range (WIERSZE):
			if getJewelZPozycji(kopiaSiatki, x, y) == getJewelZPozycji(kopiaSiatki, x + 1, y) == getJewelZPozycji(kopiaSiatki, x + 2, y) and getJewelZPozycji(kopiaSiatki, x, y) != PUSTE_MIEJSCE:
				wybranyJewel = kopiaSiatki[x][y]
				przesuniecie = 0
				zbiorUsuniecia = []
				while getJewelZPozycji(kopiaSiatki, x + przesuniecie, y) == wybranyJewel:
					zbiorUsuniecia.append((x + przesuniecie, y))
					kopiaSiatki[x + przesuniecie][y] = PUSTE_MIEJSCE
					przesuniecie += 1
				jeweleDoUsuniecia.append(zbiorUsuniecia)
			
			if getJewelZPozycji(kopiaSiatki, x, y) == getJewelZPozycji(kopiaSiatki, x, y + 1) == getJewelZPozycji(kopiaSiatki, x, y + 2) and getJewelZPozycji(kopiaSiatki, x, y) != PUSTE_MIEJSCE:
				wybranyJewel = kopiaSiatki[x][y]
				przesuniecie = 0
				zbiorUsuniecia = []
				while getJewelZPozycji(kopiaSiatki, x, y + przesuniecie) == wybranyJewel:
					zbiorUsuniecia.append((x, y + przesuniecie))
					kopiaSiatki[x][y + przesuniecie] = PUSTE_MIEJSCE
					przesuniecie += 1
				jeweleDoUsuniecia.append(zbiorUsuniecia)
	return jeweleDoUsuniecia
			
def ustawZamienianeJewele(siatka, piJewelPoz, drJewelPoz):
	pierwszyJewel = {'rodzajJewela': siatka[piJewelPoz['x']][piJewelPoz['y']], 
				'x': piJewelPoz['x'], 
				'y': piJewelPoz['y']}
	drugiJewel = {'rodzajJewela': siatka[drJewelPoz['x']][drJewelPoz['y']],
				'x': drJewelPoz['x'],
				'y': drJewelPoz['y']}
	if pierwszyJewel['x'] == drugiJewel['x'] + 1 and pierwszyJewel['y'] == drugiJewel['y']:
		pierwszyJewel['kierunek'] = LE
		drugiJewel['kierunek'] = PR
	elif pierwszyJewel['x'] == drugiJewel['x'] - 1 and pierwszyJewel['y'] == drugiJewel['y']:
		pierwszyJewel['kierunek'] = PR
		drugiJewel['kierunek'] = LE
	elif  pierwszyJewel['x'] == drugiJewel['x'] and pierwszyJewel['y'] == drugiJewel['y'] + 1:
		pierwszyJewel['kierunek'] = GO
		drugiJewel['kierunek'] = DO
	elif  pierwszyJewel['x'] == drugiJewel['x'] and pierwszyJewel['y'] == drugiJewel['y'] - 1:
		pierwszyJewel['kierunek'] = DO
		drugiJewel['kierunek'] = GO
	else:
		return None, None
	return pierwszyJewel, drugiJewel
		
def sprawdzCzyKliknietoJewela(pos):
	for x in range(KOLUMNY):
		for y in range (WIERSZE):
			if JEWEL_RAMKI[x][y].collidepoint(pos[0], pos[1]):
				return {'x': x, 'y': y}
	return None

		
def getPustaSiatka():
	siatka = []
	for x in range(KOLUMNY):
		siatka.append([PUSTE_MIEJSCE] * WIERSZE)
	return siatka

def wypelnijSiatkeJewelami(siatka, punkty, wynik):
	kolumnyWypelniajace = getKolumnyWypelniajace(siatka)
	licznik = 0;
	while kolumnyWypelniajace != [[]] * KOLUMNY:
		#print 'bugbug', [[]] * KOLUMNY

		ruchomeJewele = getSpadajaceJewele(siatka)
		for x in range(len(kolumnyWypelniajace)):
			if len(kolumnyWypelniajace[x]) != 0:
				ruchomeJewele.append({'rodzajJewela': kolumnyWypelniajace[x][0], 'x': x, 'y': WIERSZ_NAD_PLANSZA, 'kierunek': DO})
		kopiaSiatki = getKopiaSiatkiBezNiektorychJeweli(siatka, ruchomeJewele)
		animujJewele(kopiaSiatki, ruchomeJewele, punkty, wynik)
		licznik += 1
		#print 'licznik', licznik
		przesunJewele(siatka, ruchomeJewele)
       	
       	
		for x in range(len(kolumnyWypelniajace)):
			if len(kolumnyWypelniajace[x]) == 0:
				continue
			elif len(kolumnyWypelniajace[x]) != 0: 	
				siatka[x][0] = kolumnyWypelniajace[x][0]
				del kolumnyWypelniajace[x][0]		
				
				
def sciagnijJewele(siatka):
	for x in range(KOLUMNY):
		jeweleWKolumnie = []
		for y in range(WIERSZE):
			if siatka[x][y] != PUSTE_MIEJSCE:
				jeweleWKolumnie.append(siatka[x][y])
		siatka[x] = ([PUSTE_MIEJSCE] * (WIERSZE - len(jeweleWKolumnie))) + jeweleWKolumnie
		

def getKolumnyWypelniajace(siatka):
	kopiaSiatki = copy.deepcopy(siatka)
	sciagnijJewele(kopiaSiatki)
	
	spadajaceRamki = []
	
	for i in range(KOLUMNY):
		spadajaceRamki.append([])
	
	for x in range(KOLUMNY):
		for y in range(WIERSZE-1, -1, -1):  #w kolejnosci od dolu do gory
			if kopiaSiatki[x][y] == PUSTE_MIEJSCE:
				mozliweJewele = list(range(len(JEWELS_OBRAZKI)))
				for przesuniecieX, przesuniecieY in ((0, -1),(1, 0),(0, 1),(-1, 0)):
					#sprawdzamy czy nie spadna obok siebie 2 jewele tego samego koloru
					jewelSasiad = getJewelZPozycji(kopiaSiatki, x + przesuniecieX, y + przesuniecieY)
					if jewelSasiad != None and jewelSasiad in mozliweJewele:
						mozliweJewele.remove(jewelSasiad)
				
				nowyJewel = random.choice(mozliweJewele)
				
				kopiaSiatki[x][y] = nowyJewel
				spadajaceRamki[x].append(nowyJewel)
	return spadajaceRamki
	
def getJewelZPozycji(siatka, x, y):
    if x < 0 or y < 0 or x >= KOLUMNY or y >= WIERSZE:
        return None
    else:
        return siatka[x][y]	

def getSpadajaceJewele(siatka):
	#zwraca te jewele ktore powinny spasc
	kopiaSiatki = copy.deepcopy(siatka)
	spadajaceJewele = []
	for x in range (KOLUMNY):
		for y in range (WIERSZE - 2, -1, -1):
			if kopiaSiatki[x][y + 1] == PUSTE_MIEJSCE and kopiaSiatki[x][y] != PUSTE_MIEJSCE:
				spadajaceJewele.append({'rodzajJewela': kopiaSiatki[x][y], 'x': x, 'y': y, 'kierunek': DO})
				kopiaSiatki[x][y] = PUSTE_MIEJSCE
	return spadajaceJewele

def getKopiaSiatkiBezNiektorychJeweli(siatka, jewele):
	kopiaSiatki = copy.deepcopy(siatka)
	
	for jewel in jewele:
		if jewel['y'] != WIERSZ_NAD_PLANSZA:
			kopiaSiatki[jewel['x']][jewel['y']] = PUSTE_MIEJSCE
	return kopiaSiatki


def rysujSiatke(siatka):
	for x in range(KOLUMNY):
		for y in range(WIERSZE):
			ramka = JEWEL_RAMKI[x][y]
			jewelDoNarysowania = siatka[x][y]
			if jewelDoNarysowania != PUSTE_MIEJSCE:
				DISPLAYSURF.blit(JEWELS_OBRAZKI[jewelDoNarysowania], JEWEL_RAMKI[x][y])
	

def przesunJewele(siatka, ruchomeJewele):
	for jewel in ruchomeJewele:
		if jewel['y'] != WIERSZ_NAD_PLANSZA:
			siatka[jewel['x']][jewel['y']] = PUSTE_MIEJSCE
			ruch_x = 0
			ruch_y = 0
			if jewel['kierunek'] == LE:
				ruch_x = -1
			elif jewel['kierunek'] == PR:
				ruch_x = 1
			elif jewel['kierunek'] == DO:
				ruch_y = 1
			elif jewel['kierunek'] == GO:
				ruch_y = -1
			siatka[jewel['x']+ ruch_x][jewel['y'] + ruch_y] = jewel['rodzajJewela']
		else:
			siatka[jewel['x']][0] = jewel['rodzajJewela']
def rysujRuchomyJewel(jewel, krok):
	ruch_x = 0
	ruch_y = 0
	krok *= 0.01
	
	if jewel['kierunek'] == GO:
		ruch_y = - int(krok * JEWEL_ROZMIAR)
	elif jewel['kierunek'] == DO:
		ruch_y = int(krok * JEWEL_ROZMIAR)
	elif jewel['kierunek'] == PR:
		ruch_x = int(krok * JEWEL_ROZMIAR)
	elif jewel['kierunek'] == LE:
		ruch_x = - int(krok * JEWEL_ROZMIAR)
	

	j_x = jewel['x']
	j_y = jewel['y']
	if j_y == WIERSZ_NAD_PLANSZA:
		j_y = -1

	pixel_x = MARGINES_X + (j_x * JEWEL_ROZMIAR)
	pixel_y = MARGINES_Y + (j_y * JEWEL_ROZMIAR)
	ramka = pygame.Rect( (pixel_x + ruch_x, pixel_y + ruch_y, JEWEL_ROZMIAR, JEWEL_ROZMIAR) )
	DISPLAYSURF.blit(JEWELS_OBRAZKI[jewel['rodzajJewela']], ramka)

def rysujWynik(wynik):
    wynikObrazek = CZCIONKA.render(str(wynik), 1, KOLOR_WYNIKU)
    wynikRamka = wynikObrazek.get_rect()
    wynikRamka.bottomleft = (10, WYSOKOSC_OKNA - 6)
    DISPLAYSURF.blit(wynikObrazek, wynikRamka)	
		
def animujJewele(siatka, jewele, punkty, wynik):
	stan = 0 
	while stan <= 100: # petla animacji
		
		tlo =  pygame.image.load('tlo.png')
		rr = pygame.Rect(0,0,800,480)
		DISPLAYSURF.blit(tlo, rr)
		
		rysujSiatke(siatka)
		for jewel in jewele: 
			rysujRuchomyJewel(jewel, stan)
		rysujWynik(wynik)
		for punkt in punkty:
			punktySurf = CZCIONKA.render(str(punkty['punkty']), 1, KOLOR_WYNIKU)
			punktyRamka = punktySurf.get_rect()
			punktyRamka.center = (punkty['x'], punkty['y'])
			DISPLAYSURF.blit(punktySurf, punktyRamka)

		pygame.display.update()
		FPSZEGAR.tick(FPS)
		stan += SZYBKOSC_ANIMACJI 

def istniejaRuchy(siatka):

    pattern         = (((0,1), (1,0), (2,0)),
                      ((0,1), (1,1), (2,0)),
                      ((0,0), (1,1), (2,0)),
                      ((0,1), (1,0), (2,1)),
                      ((0,0), (1,0), (2,1)),
                      ((0,0), (1,1), (2,1)),
                      ((0,0), (0,2), (0,3)),
                      ((0,0), (0,1), (0,3)))



    for x in range(KOLUMNY):
        for y in range(WIERSZE):
            for pat in pattern:

                if (getJewelZPozycji(siatka, x+pat[0][0], y+pat[0][1]) == \
                    getJewelZPozycji(siatka, x+pat[1][0], y+pat[1][1]) == \
                    getJewelZPozycji(siatka, x+pat[2][0], y+pat[2][1]) != None) or \
                   (getJewelZPozycji(siatka, x+pat[0][1], y+pat[0][0]) == \
                    getJewelZPozycji(siatka, x+pat[1][1], y+pat[1][0]) == \
                    getJewelZPozycji(siatka, x+pat[2][1], y+pat[2][0]) != None):
                    return True 
    return False		
		
if __name__ == '__main__':
	main()
