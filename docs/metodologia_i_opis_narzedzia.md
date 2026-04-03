# Emission Impossible — Metodologia i opis narzędzia

## Kalkulator śladu węglowego organizacji zgodny z GHG Protocol

---

## Spis treści

1. [Dlaczego ślad węglowy ma znaczenie](#1-dlaczego-ślad-węglowy-ma-znaczenie)
2. [Metodologia — GHG Protocol](#2-metodologia--ghg-protocol)
3. [Zakres 1 — Emisje bezpośrednie](#3-zakres-1--emisje-bezpośrednie)
4. [Zakres 2 — Emisje pośrednie z energii](#4-zakres-2--emisje-pośrednie-z-energii)
5. [Korzyści ze świadomego zarządzania emisjami](#5-korzyści-ze-świadomego-zarządzania-emisjami)
6. [Transparentna komunikacja ze społeczeństwem](#6-transparentna-komunikacja-ze-społeczeństwem)
7. [Opis narzędzia Emission Impossible](#7-opis-narzędzia-emission-impossible)
8. [Funkcjonalności i zalety narzędzia](#8-funkcjonalności-i-zalety-narzędzia)
9. [Problemy, które rozwiązuje narzędzie](#9-problemy-które-rozwiązuje-narzędzie)
10. [Przypadki użycia](#10-przypadki-użycia)
11. [Ciekawostki i anegdoty](#11-ciekawostki-i-anegdoty)
12. [Instrukcja — Przewodnik po danych emisyjnych](#12-instrukcja--przewodnik-po-danych-emisyjnych)

---

## 1. Dlaczego ślad węglowy ma znaczenie

### Czym jest ślad węglowy?

Ślad węglowy (ang. *carbon footprint*) to łączna ilość gazów cieplarnianych emitowanych bezpośrednio i pośrednio przez organizację, produkt, usługę lub osobę, wyrażona w **tonach ekwiwalentu dwutlenku węgla (tCO₂e)**. Ekwiwalent CO₂ pozwala porównywać różne gazy cieplarniane — metan, podtlenek azotu, freony — przeliczając je na wspólną miarę ich wpływu na klimat.

### Dlaczego firmy powinny liczyć swój ślad węglowy?

**Wymogi regulacyjne i prawne:**
- Dyrektywa CSRD (Corporate Sustainability Reporting Directive) nakłada na coraz więcej firm w UE obowiązek raportowania emisji od 2025 roku. Dotyczy to dużych spółek, a od 2026 roku również notowanych MŚP.
- Taksonomia UE wymaga od firm ujawniania, w jakim stopniu ich działalność jest zrównoważona środowiskowo.
- Krajowe regulacje — w Polsce raporty środowiskowe są wymagane m.in. przez ustawę o systemie handlu uprawnieniami do emisji gazów cieplarnianych.

**Wymogi rynkowe i łańcucha dostaw:**
- Duże korporacje coraz częściej wymagają od swoich dostawców raportowania emisji. Firma, która nie potrafi podać swojego śladu węglowego, może stracić kontrakty.
- Instytucje finansowe i fundusze inwestycyjne uwzględniają ryzyko klimatyczne w decyzjach kredytowych i inwestycyjnych. Emisyjność firmy wpływa na jej ocenę ESG i dostęp do kapitału.

**Wiedza, którą zyskujemy:**
- **Gdzie tracimy pieniądze** — każda tona CO₂ to spalony surowiec, zużyta energia, utracone zasoby. Identyfikacja źródeł emisji to jednocześnie mapa potencjalnych oszczędności.
- **Gdzie są ryzyka** — uzależnienie od paliw kopalnych to ryzyko cenowe i regulacyjne. Firmy o wysokiej emisyjności są bardziej narażone na koszty uprawnień do emisji i podatki węglowe.
- **Jak wypadamy na tle branży** — benchmarking emisyjny pozwala ocenić pozycję konkurencyjną i zidentyfikować liderów dekarbonizacji.
- **Czy nasze działania przynoszą efekt** — śledzenie emisji rok do roku pokazuje, czy wdrożone inicjatywy (wymiana kotłów, fotowoltaika, optymalizacja logistyki) faktycznie redukują ślad węglowy.
- **Jak planować przyszłość** — dane historyczne pozwalają budować scenariusze redukcji i wyznaczać realistyczne cele klimatyczne (np. zgodne z Science Based Targets initiative).

---

## 2. Metodologia — GHG Protocol

### Standard GHG Protocol

GHG Protocol (Greenhouse Gas Protocol) to najszerzej stosowany na świecie standard raportowania emisji gazów cieplarnianych. Został opracowany wspólnie przez **World Resources Institute (WRI)** i **World Business Council for Sustainable Development (WBCSD)** w 2001 roku.

Standard dzieli emisje organizacji na **trzy zakresy (Scopes)**:

**Scope 1** - emisję bezpośrednie np. Spalanie gazu w kotłowni, paliwo we flocie firmowej 
**Scope 2** - emisje pośrednie z energii np. Zakupiona energia elektryczna, ciepło sieciowe
**Scope 3** - Inne pośrednie np. Transport dostawców, podróże służbowe, odpady

Narzędzie Emission Impossible obsługuje **Zakres 1 i Zakres 2** — te dwa zakresy stanowią rdzeń raportowania emisyjnego i są wymagane przez większość regulacji.

### Zasady GHG Protocol

1. **Istotność (Relevance)** — raport powinien odzwierciedlać faktyczny profil emisyjny firmy.
2. **Kompletność (Completeness)** — uwzględnienie wszystkich istotnych źródeł emisji.
3. **Spójność (Consistency)** — ta sama metodologia rok do roku umożliwia porównywanie trendów.
4. **Przejrzystość (Transparency)** — jasne wskazanie źródeł danych, wskaźników i założeń.
5. **Dokładność (Accuracy)** — minimalizacja błędów i niepewności pomiarowych.

### Jednostka miary

Wszystkie emisje wyrażane są w **tonach ekwiwalentu CO₂ (tCO₂e)**. Dla gazów innych niż CO₂ stosuje się współczynniki GWP (Global Warming Potential) z raportów IPCC — np. metan (CH₄) ma GWP = 28, co oznacza, że 1 tona metanu odpowiada 28 tonom CO₂ pod względem wpływu na klimat.

### Wzory obliczeniowe

Podstawowy wzór na emisje to:

```
Emisja [tCO₂e] = Dane aktywności [jednostka] × Wskaźnik emisji [tCO₂e/jednostka]
```

Przykłady:
- `12 000 m³ gazu ziemnego × 0,00202 tCO₂e/m³ = 24,24 tCO₂e`
- `450 MWh energii elektrycznej × 0,709 tCO₂e/MWh = 319,05 tCO₂e`
- `5 kg czynnika R410A × 2 088 kgCO₂e/kg = 10,44 tCO₂e`

---

## 3. Zakres 1 — Emisje bezpośrednie

### Definicja

Zakres 1 (Scope 1) obejmuje **emisje gazów cieplarnianych ze źródeł będących własnością lub pod kontrolą organizacji**. Są to emisje, które fizycznie powstają na terenie firmy lub w jej pojazdach.

### Kategorie Zakresu 1

#### 3.1 Spalanie stacjonarne

**Co to jest?** Emisje ze spalania paliw w stacjonarnych źródłach — kotły grzewcze, piece przemysłowe, turbiny gazowe, agregaty prądotwórcze.

**Typowe źródła danych:**
- Faktury za gaz ziemny (m³ lub MWh)
- Faktury za olej opałowy, węgiel, pellet (tony, litry)
- Odczyty liczników paliwa

**Przykładowe dane w narzędziu:**

| Pole | Opis | Przykład |
|------|------|---------|
| Rok | Rok sprawozdawczy | 2025 |
| Firma | Nazwa spółki | GreenTech Produkcja |
| Paliwo | Rodzaj paliwa | gaz ziemny |
| Ilość | Zużyta ilość | 45 000 |
| Jednostka | Jednostka miary | m³ |
| Instalacja | Nazwa źródła | piec przemysłowy 1 |
| Źródło danych | Skąd pochodzi informacja | faktura |

**Dozwolone paliwa:** gaz ziemny, benzyna, diesel, LPG, węgiel kamienny, koks, olej opałowy lekki, olej opałowy ciężki, pellet, biomasa, drewno.

**Ważne:** Biomasa i drewno mają wskaźnik emisji = 0, ponieważ są uznawane za neutralne węglowo (CO₂ emitowane przy spalaniu zostało wcześniej pochłonięte przez rośliny w procesie fotosyntezy).

#### 3.2 Spalanie mobilne

**Co to jest?** Emisje ze spalania paliw w pojazdach będących własnością firmy lub leasingowanych — samochody służbowe, ciężarówki, wózki widłowe, maszyny budowlane.

**Typowe źródła danych:**
- Karty paliwowe (rozliczenie miesięczne w litrach)
- Faktury za paliwo
- Raporty z systemów GPS/telematyki floty

**Przykładowe dane:**

| Pole | Opis | Przykład |
|------|------|---------|
| Pojazd | Typ pojazdu | ciężarówka 12t |
| Paliwo | Rodzaj paliwa | diesel |
| Ilość | Zużyta ilość | 45 000 |
| Jednostka | Jednostka miary | l (litry) |
| Źródło | Skąd pochodzi informacja | karty paliwowe |

**Wskazówka praktyczna:** Jeśli firma nie mierzy zużycia paliwa bezpośrednio, można je oszacować na podstawie przejechanych kilometrów i średniego spalania pojazdów. Jednak dokładniejsze są dane z kart paliwowych lub faktur.

#### 3.3 Emisje procesowe

**Co to jest?** Emisje powstające w wyniku procesów przemysłowych, nie ze spalania paliw — np. kalcynacja wapienia (uwalnia CO₂ z węglanu wapnia), reakcje chemiczne, topienie metali, spawanie.

**Typowe źródła danych:**
- Raporty produkcyjne (ilość przetworzonego surowca w tonach)
- Dokumentacja technologiczna procesu
- Pomiary emisji na kominie (jeśli dostępne)

**Przykładowe dane:**

| Pole | Opis | Przykład |
|------|------|---------|
| Proces | Nazwa procesu | kalcynacja |
| Produkt | Co jest wytwarzane | wapno |
| Ilość | Ilość przetworzonego surowca | 100 |
| Jednostka | Jednostka miary | t |

**Ciekawostka:** W przemyśle cementowym emisje procesowe z kalcynacji wapienia stanowią ponad 60% całkowitych emisji zakładu — więcej niż spalanie paliw do ogrzewania pieców!

#### 3.4 Emisje niezorganizowane (fugitive)

**Co to jest?** Niekontrolowane wycieki gazów cieplarnianych — najczęściej czynników chłodniczych z systemów klimatyzacji i chłodnictwa, ale także wycieki metanu z instalacji gazowych.

**Typowe źródła danych:**
- Protokoły serwisowe klimatyzacji (ilość uzupełnionego czynnika = ilość, która wyciekła)
- Karty serwisowe urządzeń chłodniczych
- Raporty z systemów detekcji wycieków

**Przykładowe dane:**

| Pole | Opis | Przykład |
|------|------|---------|
| Instalacja | Nazwa urządzenia | klimatyzacja biuro główne |
| Czynnik | Typ czynnika chłodniczego | R410A |
| Ilość | Ilość wycieku | 5 |
| Jednostka | Jednostka miary | kg |

**Dlaczego to ważne?** Czynniki chłodnicze mają ekstremalnie wysoki potencjał cieplarniany (GWP). Przykłady:

| Czynnik | GWP (100-letni) | Znaczenie |
|---------|----------------|-----------|
| R410A | 2 088 | 1 kg R410A = 2,088 tony CO₂e |
| R404A | 3 922 | 1 kg R404A = 3,922 tony CO₂e |
| R32 | 675 | Nowszy, mniej szkodliwy zamiennik |

**Oznacza to, że wyciek zaledwie 5 kg czynnika R410A generuje emisję ponad 10 ton CO₂e** — tyle co spalanie ~50 000 m³ gazu ziemnego lub przejechanie samochodem ~100 000 km!

---

## 4. Zakres 2 — Emisje pośrednie z energii

### Definicja

Zakres 2 (Scope 2) obejmuje **emisje pośrednie powstające w wyniku wytwarzania zakupionej energii elektrycznej, ciepła, pary technologicznej lub chłodu** zużywanych przez organizację. Emisje te fizycznie powstają w elektrowni lub ciepłowni, ale odpowiedzialność za nie ponosi odbiorca energii.

### Dlaczego Zakres 2 jest tak istotny?

Dla większości firm usługowych i biurowych Zakres 2 stanowi **60-80% całkowitego śladu węglowego**. Nawet w przemyśle ciężkim zużycie energii elektrycznej to często drugie co do wielkości źródło emisji. Redukcja Zakresu 2 (np. przez zakup zielonej energii, fotowoltaikę, poprawę efektywności energetycznej) jest jednym z najszybszych i najłatwiejszych sposobów na zmniejszenie śladu węglowego.

### Metody obliczeniowe

GHG Protocol definiuje dwie metody obliczania Zakresu 2:

**1. Metoda location-based (oparta na lokalizacji)**
Stosuje średni wskaźnik emisji dla sieci energetycznej w danym kraju. W Polsce wskaźnik publikowany przez KOBiZE wynosi 0,709 tCO₂e/MWh (2024). Oznacza to, że statystycznie za każdą megawatogodzinę zużytą w Polsce do atmosfery trafia ~709 kg CO₂.

**2. Metoda market-based (oparta na rynku)**
Uwzględnia konkretne źródło energii zakupione przez firmę — np. zielone certyfikaty (Gwarancje Pochodzenia), umowy PPA, własną fotowoltaikę. Jeśli firma kupiła energię z OZE potwierdzoną certyfikatem GO, jej emisja z tego źródła wynosi 0.

Narzędzie Emission Impossible obsługuje obie metody — użytkownik wybiera źródło energii (Zakupiona / Wyprodukowana) i typ energii (OZE / nie OZE).

### Kategorie Zakresu 2

#### 4.1 Energia elektryczna

**Źródła danych:**
- Faktury od dostawcy energii (MWh, kWh)
- Umowy z dostawcą (czy energia jest z OZE?)
- Certyfikaty Gwarancji Pochodzenia (GO)
- Odczyty z własnej fotowoltaiki

**Wskaźniki dla Polski (KOBiZE 2024):**
- Energia z sieci (nie OZE): **0,709 tCO₂e/MWh**
- Energia z OZE (z certyfikatem GO): **0,000 tCO₂e/MWh**

#### 4.2 Energia cieplna (ciepło sieciowe)

**Źródła danych:**
- Faktury od dostawcy ciepła (GJ)
- Odczyty liczników ciepła

**Wskaźnik:** 0,292 tCO₂e/GJ (KOBiZE 2024)

#### 4.3 Para technologiczna

Stosowana w procesach przemysłowych. Wskaźnik: 0,292 tCO₂e/GJ.

#### 4.4 Chłód

Zakupiony chłód (np. z sieci chłodniczej). Wskaźnik: 0,180 tCO₂e/GJ.

### Przykładowe dane w narzędziu:

| Pole | Opis | Przykład |
|------|------|---------|
| Rok | Rok sprawozdawczy | 2025 |
| Firma | Nazwa spółki | GreenTech Polska |
| Ilość | Zużyta ilość | 450 |
| Jednostka | MWh, kWh, GJ, MJ | MWh |
| Źródło energii | Zakupiona / Wyprodukowana / Sprzedana | Zakupiona |
| Typ energii | Rodzaj energii | Energia elektryczna nie OZE |
| Źródło danych | Skąd informacja | faktura |

---

## 5. Korzyści ze świadomego zarządzania emisjami

### Korzyści finansowe

- **Redukcja kosztów energii** — identyfikacja marnotrawstwa energetycznego prowadzi do konkretnych oszczędności. Firmy, które wdrożyły systematyczne zarządzanie energią, raportują oszczędności rzędu 10-30%.
- **Unikanie kar i opłat** — system EU ETS (handel uprawnieniami do emisji) oznacza realne koszty emisji. W 2024 roku cena uprawnienia wynosiła ~60-80 EUR/tCO₂. Firma emitująca 1000 tCO₂e rocznie wydaje 60-80 tys. EUR na uprawnienia.
- **Dostęp do zielonego finansowania** — banki oferują preferencyjne warunki kredytowe dla firm z niskim śladem węglowym. Zielone obligacje (green bonds) to rosnący rynek wart ponad 500 mld USD rocznie.
- **Wyższa wycena firmy** — badania pokazują, że firmy z dobrymi wynikami ESG mają średnio 10-15% wyższą wycenę giełdową niż ich odpowiednicy bez strategii klimatycznej.

### Korzyści operacyjne

- **Odporność na szoki cenowe** — firma, która zdywersyfikowała źródła energii i zmniejszyła zużycie paliw kopalnych, jest mniej narażona na wahania cen ropy i gazu.
- **Optymalizacja procesów** — pomiar emisji wymusza analizę procesów, co często prowadzi do odkrycia nieefektywności operacyjnych.
- **Lepsze zarządzanie ryzykiem** — świadomość profilu emisyjnego pozwala planować przejście na niskoemisyjne technologie w kontrolowany sposób, zamiast reagować na nagłe zmiany regulacyjne.

### Korzyści wizerunkowe i rynkowe

- **Przewaga konkurencyjna** — w przetargach publicznych i korporacyjnych coraz częściej wymagany jest raport emisyjny. Firma z gotowym raportem wygrywa z tą, która go nie ma.
- **Przyciąganie talentów** — badania Deloitte (2024) pokazują, że 70% pracowników z pokolenia Z preferuje pracodawców ze strategią klimatyczną.
- **Lojalność klientów** — 65% konsumentów deklaruje gotowość do płacenia więcej za produkty od firm odpowiedzialnych środowiskowo (Nielsen, 2023).

---

## 6. Transparentna komunikacja ze społeczeństwem

### Dlaczego otwartość się opłaca?

W erze mediów społecznościowych i natychmiastowego dostępu do informacji, greenwashing (fałszywe deklaracje ekologiczne) jest szybko demaskowany i niesie poważne konsekwencje wizerunkowe. Transparentna komunikacja oparta na twardych danych to jedyna wiarygodna strategia.

### Zasady skutecznej komunikacji klimatycznej

1. **Opieraj się na danych, nie na hasłach** — zamiast "jesteśmy eko", powiedz "w 2025 roku zredukowaliśmy emisje o 15% w porównaniu do 2023 roku".
2. **Pokazuj trendy, nie tylko wyniki** — wykres spadku emisji rok do roku jest bardziej przekonujący niż jednorazowa deklaracja.
3. **Bądź szczery w kwestii wyzwań** — firma, która mówi "w tym obszarze mamy jeszcze dużo do zrobienia" budzi większe zaufanie niż ta, która prezentuje wyłącznie sukcesy.
4. **Angażuj interesariuszy** — pracownicy, klienci, społeczność lokalna — każda z tych grup oczekuje innego poziomu szczegółowości i formy komunikacji.

### Przykłady dobrych praktyk

- **Raport roczny z emisji** — publikacja śladu węglowego organizacji w raporcie ESG, z podziałem na Zakres 1 i 2, porównaniem rok do roku, opisem podjętych działań redukcyjnych.
- **Kalkulatory emisji dla klientów** — udostępnienie klientom informacji o śladzie węglowym produktu/usługi.
- **Cele redukcyjne** — publiczne zobowiązanie do redukcji emisji o X% do roku Y, najlepiej zatwierdzone przez Science Based Targets initiative (SBTi).

---

## 7. Opis narzędzia Emission Impossible

### Czym jest Emission Impossible?

Emission Impossible to **kalkulator śladu węglowego organizacji** — narzędzie do zbierania danych o zużyciu paliw i energii, automatycznego obliczania emisji gazów cieplarnianych i generowania raportów emisyjnych zgodnych z metodologią GHG Protocol.

### Dla kogo jest to narzędzie?

- **Specjaliści ds. ESG i środowiska** — codzienne narzędzie pracy do zbierania i przetwarzania danych emisyjnych.
- **Dyrektorzy finansowi (CFO)** — szybki wgląd w koszty emisyjne i potencjał oszczędności.
- **Zarządy spółek** — dashboard z kluczowymi wskaźnikami emisyjnymi dla podejmowania decyzji strategicznych.
- **Grupy kapitałowe** — konsolidacja danych emisyjnych z wielu spółek w jednym narzędziu.
- **Audytorzy i doradcy** — weryfikacja danych emisyjnych i identyfikacja problemów z jakością danych.

### Architektura narzędzia

Narzędzie opiera się na **warstwowej architekturze** zapewniającej separację odpowiedzialności:

```
CLI (interfejs użytkownika)
    ↓
Logika biznesowa (obliczenia, raporty, walidacja)
    ↓
Warstwa danych (repozytoria CSV / docelowo SQL)
    ↓
Pliki danych (CSV) lub baza danych
```

Taka architektura oznacza, że:
- Zmiana interfejsu (np. na webowy) nie wymaga przebudowy logiki obliczeń.
- Migracja z CSV na bazę SQL wymaga jedynie podmianki warstwy danych.
- Obliczenia są testowalne jednostkowo — 128 automatycznych testów weryfikuje poprawność obliczeń.

---

## 8. Funkcjonalności i zalety narzędzia

### Główne funkcjonalności

**Zbieranie danych:**
- Interaktywne dodawanie rekordów emisyjnych z walidacją danych wejściowych
- Obsługa wszystkich kategorii Zakresu 1 (spalanie stacjonarne, mobilne, emisje procesowe, fugitive) i Zakresu 2 (energia elektryczna, ciepło, para, chłód)
- Automatyczna walidacja typów paliw, jednostek, zakresów dat
- Podgląd szacunkowej emisji już przy wprowadzaniu danych

**Obliczenia:**
- Automatyczne przeliczanie emisji na podstawie wskaźników emisji (KOBiZE, DEFRA, IPCC)
- Automatyczna konwersja jednostek (np. kWh → MWh, kg → t)
- Obliczenia wykonywane w pamięci — dane źródłowe w CSV nie są nadpisywane
- Obsługa wskaźnika raportowego (raport=TRUE → wartość podana przez użytkownika, raport=FALSE → obliczenie automatyczne)

**Raportowanie:**
- Podsumowanie emisji Scope 1 + Scope 2 dla pojedynczej spółki lub całej grupy kapitałowej
- Raport trendów rok do roku z procentową zmianą emisji
- Wykresy porównawcze (słupkowy) i strukturalne (kołowy)
- Wykres trendów (liniowy)
- Eksport raportów do CSV

**Zarządzanie danymi:**
- System ról (admin / użytkownik) z kontrolą dostępu na poziomie spółki
- Walidacja spójności danych (czy firmy w danych emisyjnych istnieją w rejestrze firm)
- Weryfikacja kompletności wskaźników i przeliczników
- Automatyczne kopie zapasowe przy każdej modyfikacji danych

### Zalety narzędzia

| Cecha | Korzyść |
|-------|---------|
| **Obliczenia w pamięci** | Dane źródłowe nie są nadpisywane — zawsze możesz wrócić do oryginału |
| **Automatyczne przeliczanie jednostek** | Nie musisz ręcznie konwertować kWh na MWh czy kg na tony |
| **128 testów automatycznych** | Pewność, że obliczenia są poprawne — każda zmiana kodu jest weryfikowana |
| **Wielospółkowość** | Jedna instalacja obsługuje całą grupę kapitałową |
| **Polskie wskaźniki emisji** | KOBiZE 2024, DEFRA 2024, IPCC AR5 — aktualne i wiarygodne źródła |
| **Kontrola dostępu** | Każdy użytkownik widzi tylko swoje spółki |
| **Eksport CSV** | Łatwy import do Excela, Power BI, innych narzędzi analitycznych |
| **Open source** | Pełna transparentność metodologii — audytor może zweryfikować każdy wzór |

---

## 9. Problemy, które rozwiązuje narzędzie

### Problem 1: „Mamy dane w Excelu, ale nikt nie wie, jak policzyć emisje"

**Sytuacja:** Firma zbiera faktury za gaz, prąd, paliwo, ale przeliczanie ich na tCO₂e wymaga znajomości wskaźników, konwersji jednostek i metodologii GHG Protocol.

**Rozwiązanie:** Emission Impossible automatyzuje cały proces — wystarczy wpisać ilość i jednostkę, a narzędzie samo dobierze wskaźnik emisji i przeliczy wynik.

### Problem 2: „Każda spółka w grupie liczy emisje inaczej"

**Sytuacja:** W grupie kapitałowej każda spółka używa własnego arkusza Excel, własnych wskaźników, własnego formatu. Konsolidacja danych trwa tygodnie i jest obarczona błędami.

**Rozwiązanie:** Jedno narzędzie ze wspólną bazą wskaźników, jednolitą metodologią i automatyczną konsolidacją na poziomie grupy.

### Problem 3: „Nie wiemy, czy nasze dane są poprawne"

**Sytuacja:** Ktoś wpisał zużycie gazu w kWh zamiast m³, albo podał emisję dla złej spółki. Błędy w danych prowadzą do nieprawidłowych raportów.

**Rozwiązanie:** Wielopoziomowa walidacja — Pydantic sprawdza typy i zakresy, system uprawnień chroni przed dostępem do cudzych danych, walidacja spójności wykrywa brakujące firmy i niespójne wskaźniki.

### Problem 4: „Zarząd chce wiedzieć, czy emisje spadają, ale nie mamy porównania rok do roku"

**Sytuacja:** Firma liczy emisje ad hoc, bez systematycznego śledzenia trendów. Nie da się powiedzieć, czy działania redukcyjne przynoszą efekt.

**Rozwiązanie:** Raport trendów rok do roku z procentową zmianą, wykresy liniowe pokazujące kierunek zmian, eksport do CSV do dalszej analizy.

### Problem 5: „Audytor żąda udokumentowania metodologii"

**Sytuacja:** Przy weryfikacji raportu ESG audytor chce wiedzieć, skąd pochodzą wskaźniki, jakie wzory zostały użyte, czy dane są spójne.

**Rozwiązanie:** Przejrzysta baza wskaźników (z podanym źródłem: KOBiZE, DEFRA, IPCC), walidacja kompletności wskaźników, automatyczne testy poprawności obliczeń, pełna dokumentacja metodologiczna.

---

## 10. Przypadki użycia

### Przypadek 1: Roczny raport emisyjny

Specjalista ds. ESG loguje się, wybiera zakres lat 2025, uruchamia raport dla całej organizacji. Narzędzie automatycznie przelicza wszystkie dane, generuje podsumowanie z podziałem na Scope 1 i 2, oferuje wykresy porównawcze i eksport do CSV. Dane trafiają do raportu CSRD.

### Przypadek 2: Due diligence przy przejęciu

Firma rozważa przejęcie spółki produkcyjnej. Analityk wprowadza dane emisyjne przejmowanej firmy do narzędzia, generuje raport trendów za ostatnie 3 lata, identyfikuje główne źródła emisji i szacuje koszty uprawnień EU ETS.

### Przypadek 3: Optymalizacja floty

Manager logistyki analizuje emisje ze spalania mobilnego — widzi, że ciężarówki 18t spalające diesel generują 70% emisji floty. To argument za wymianą na pojazdy LNG lub elektryczne.

### Przypadek 4: Przejście na OZE

Dyrektor finansowy porównuje scenariusze: obecne zużycie 4800 MWh energii nie-OZE generuje 3403 tCO₂e. Przejście na zieloną energię z certyfikatem GO redukuje Scope 2 do zera — oszczędność na uprawnieniach EU ETS: ~200-270 tys. EUR rocznie.

---

## 11. Ciekawostki i anegdoty

### Dlaczego nazwa „Emission Impossible"?

Nawiązanie do kultowego filmu „Mission: Impossible" — bo redukcja emisji do zera wydaje się misją niemożliwą, ale z odpowiednimi narzędziami i danymi staje się osiągalna. Twoja misja, jeśli zdecydujesz się ją przyjąć: policzyć, zredukować i zaraportować.

### Czynnik chłodniczy groźniejszy niż flota ciężarówek

Wyciek 10 kg czynnika R404A z systemu chłodniczego supermarketu generuje emisję **39,2 tCO₂e** — tyle co spalenie **14 600 litrów diesla** w ciężarówce, czyli przejechanie nią **~73 000 km** (prawie dwa razy dookoła Ziemi). Dlatego serwis klimatyzacji to nie tylko komfort — to zarządzanie emisjami.

### Polska na tle Europy

Polska ma jeden z najwyższych wskaźników emisji z energii elektrycznej w UE — **0,709 tCO₂e/MWh** (2024). Dla porównania: Francja ~0,055 (dzięki energii jądrowej), Szwecja ~0,013 (hydroenergetyka i wiatr), Niemcy ~0,380. To oznacza, że ta sama fabryka przeniesiona z Polski do Francji miałaby **13 razy niższy Scope 2** — nie dlatego, że jest efektywniejsza, ale dlatego, że sieć energetyczna jest czystsza.

### Biomasa — darmowa emisja?

Wskaźnik emisji dla biomasy i drewna wynosi 0 tCO₂e/t. Czy to znaczy, że spalanie drewna nie emituje CO₂? Emituje — i to sporo. Jednak według konwencji GHG Protocol emisje te są „neutralne", ponieważ CO₂ zostało wcześniej pochłonięte z atmosfery przez rosnące drzewa. To tzw. „krótki cykl węglowy" — w przeciwieństwie do paliw kopalnych, gdzie uwalniany jest węgiel zmagazynowany miliony lat temu.

### Pierwsza firma, która policzyła swój ślad węglowy

W 1998 roku brytyjska firma energetyczna **BP** (tak, ta od ropy naftowej) jako pierwsza duża korporacja publicznie ogłosiła swój ślad węglowy i zobowiązała się do jego redukcji. Ironicznie, BP później spopularyzowało pojęcie „personal carbon footprint" w kampanii reklamowej, przenosząc odpowiedzialność na konsumentów — co stało się jednym z najbardziej kontrowersyjnych przykładów greenwashingu w historii.

### Koszt „nic nie robienia"

Według Stern Review (2006) — jednego z najważniejszych raportów ekonomicznych o zmianach klimatu — koszt bierności wobec zmian klimatu to **5-20% globalnego PKB rocznie**. Koszt działania? Około **1% PKB**. Kalkulacja jest prosta: każda złotówka wydana na redukcję emisji dziś oszczędza 5-20 złotych kosztów przyszłych szkód klimatycznych.

### Scope 3 — niewidzialny gigant

Zakresy 1 i 2 to zwykle zaledwie **20-30% całkowitego śladu węglowego firmy**. Pozostałe 70-80% to Zakres 3 — emisje w łańcuchu wartości: transport dostawców, podróże służbowe, dojazdy pracowników, zużycie produktów przez klientów, utylizacja. To temat na przyszłość, ale warto o nim wspomnieć — pełen obraz wymaga wszystkich trzech zakresów.

---

## 12. Instrukcja — Przewodnik po danych emisyjnych

> Ten rozdział służy jako baza do interaktywnego przewodnika w aplikacji — wyjaśnienia wyświetlane użytkownikowi podczas wprowadzania danych.

### Ogólne zasady wprowadzania danych

1. **Rok sprawozdawczy** — rok, w którym nastąpiło zużycie paliwa/energii (nie rok faktury). Jeśli faktura za grudzień 2024 przyszła w styczniu 2025, dane dotyczą roku 2024.
2. **Firma** — nazwa spółki prawnej, do której przypisany jest dany koszt/zużycie. W grupie kapitałowej każda spółka raportuje oddzielnie.
3. **Ilość i jednostka** — zawsze podawaj w jednostce z dokumentu źródłowego (faktury). Narzędzie automatycznie przeliczy jeśli potrzeba.
4. **Źródło danych** — podaj skąd pochodzi informacja (faktura, karta paliwowa, odczyt licznika, szacunek). Pomaga to audytorowi zweryfikować dane.

### Spalanie stacjonarne — co wpisać?

| Pytanie | Jak znaleźć odpowiedź |
|---------|----------------------|
| Jaki rodzaj paliwa? | Sprawdź na fakturze — gaz ziemny, olej opałowy, węgiel itp. |
| Ile zużyto? | Ilość z faktury — m³ gazu, tony węgla, litry oleju |
| Jaka instalacja? | Nazwa kotła, pieca, turbiny — pomaga zidentyfikować źródło |
| Mam gotową emisję? | Jeśli masz wynik z pomiaru na kominie (np. z raportu KOBIZE) — wybierz TAK i wpisz wartość. Jeśli nie — narzędzie obliczy automatycznie. |

### Spalanie mobilne — co wpisać?

| Pytanie | Jak znaleźć odpowiedź |
|---------|----------------------|
| Jaki pojazd? | Typ pojazdu — samochód osobowy, ciężarówka 12t, wózek widłowy |
| Jakie paliwo? | Benzyna, diesel, LPG — z karty paliwowej lub faktury |
| Ile paliwa? | Litry — z karty paliwowej lub faktury za paliwo |

**Wskazówka:** Jeśli nie masz danych o zużyciu paliwa, ale masz przejechane kilometry, skontaktuj się z działem floty — przebiegi można przeliczyć na litry paliwa.

### Emisje procesowe — co wpisać?

| Pytanie | Jak znaleźć odpowiedź |
|---------|----------------------|
| Jaki proces? | Nazwa procesu technologicznego — kalcynacja, synteza, topienie |
| Jaki produkt? | Co jest wytwarzane — wapno, kwas, metal |
| Ile przetworzone? | Tony surowca/produktu — z raportów produkcyjnych |

### Emisje niezorganizowane — co wpisać?

| Pytanie | Jak znaleźć odpowiedź |
|---------|----------------------|
| Jaka instalacja? | Nazwa systemu — klimatyzacja biuro, chłodnia magazyn |
| Jaki czynnik? | Typ czynnika chłodniczego — R410A, R32, R404A — z karty serwisowej |
| Ile wyciekło? | Ilość uzupełnionego czynnika (kg) = ilość wycieku — z protokołu serwisu |

**Ważne:** Jeśli nie było serwisu i uzupełnienia czynnika w danym roku — emisja fugitive = 0 dla tej instalacji.

### Zużycie energii (Scope 2) — co wpisać?

| Pytanie | Jak znaleźć odpowiedź |
|---------|----------------------|
| Źródło energii | Zakupiona (z sieci), Wyprodukowana (własna PV), Sprzedana |
| Typ energii | Energia elektryczna (OZE/nie OZE), ciepło, para, chłód |
| Ile? | MWh lub GJ — z faktury od dostawcy energii |
| OZE czy nie? | Sprawdź umowę z dostawcą — czy masz certyfikat Gwarancji Pochodzenia (GO)? Jeśli tak → OZE (emisja = 0). Jeśli nie → nie OZE. |

**Ważna uwaga o OZE:** Sam fakt, że dostawca „oferuje zieloną energię" nie wystarczy. Liczy się certyfikat Gwarancji Pochodzenia (GO) — formalny dokument potwierdzający, że konkretna ilość energii pochodzi ze źródła odnawialnego. Bez GO, nawet jeśli dostawca reklamuje się jako „zielony", energia powinna być raportowana jako nie-OZE.

### Słowniczek terminów

| Termin | Znaczenie |
|--------|-----------|
| **tCO₂e** | Tona ekwiwalentu CO₂ — uniwersalna jednostka emisji |
| **GWP** | Global Warming Potential — potencjał cieplarniany gazu |
| **GHG Protocol** | Greenhouse Gas Protocol — międzynarodowy standard raportowania |
| **KOBiZE** | Krajowy Ośrodek Bilansowania i Zarządzania Emisjami — źródło polskich wskaźników |
| **DEFRA** | Department for Environment, Food and Rural Affairs (UK) — źródło wskaźników dla paliw |
| **IPCC** | Intergovernmental Panel on Climate Change — źródło współczynników GWP |
| **EU ETS** | European Union Emissions Trading System — handel uprawnieniami do emisji |
| **CSRD** | Corporate Sustainability Reporting Directive — dyrektywa UE o raportowaniu ESG |
| **SBTi** | Science Based Targets initiative — inicjatywa wyznaczania celów klimatycznych |
| **GO** | Gwarancja Pochodzenia — certyfikat potwierdzający źródło energii odnawialnej |
| **PPA** | Power Purchase Agreement — umowa na zakup energii bezpośrednio od producenta |
| **Scope 1** | Emisje bezpośrednie (spalanie paliw, wycieki czynników, procesy) |
| **Scope 2** | Emisje pośrednie z zakupionej energii |
| **Scope 3** | Emisje pośrednie z łańcucha wartości |

---

*Dokument przygotowany na potrzeby prezentacji narzędzia Emission Impossible.*
*Metodologia zgodna z GHG Protocol Corporate Standard (Revised Edition).*
*Wskaźniki emisji: KOBiZE 2024, DEFRA 2024, IPCC AR5.*
