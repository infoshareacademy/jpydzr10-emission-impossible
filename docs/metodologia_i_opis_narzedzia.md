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
13. [Komunikacja e-mail — zapytania o dane](#13-komunikacja-e-mail--zapytania-o-dane)

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
| Emisja [tCO2eq] | Deklarowana emisja (opcjonalnie) | 24.240 |
| Raport | Źródło raportu emisji (wymagane jeśli emisja podana) | KOBiZE |
| Uwagi | Notatki do rekordu (opcjonalnie) | pomiar kontrolny |

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
| Emisja [tCO2eq] | Deklarowana emisja (opcjonalnie) | 5.568 |
| Raport | Źródło raportu (wymagane jeśli emisja podana) | DEFRA 2024 |
| Uwagi | Notatki (opcjonalnie) | flota północ |

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

Narzędzie Emission Impossible obsługuje obie metody — użytkownik wybiera typ energii (OZE / nie OZE) i rodzaj przepływu energii w osobnych tabelach.

### Kategorie Zakresu 2 w narzędziu

Zakres 2 jest podzielony na **cztery osobne tabele** odpowiadające różnym przepływom energii:

#### 4.0 Zużycie energii (`tbl_e_cons.csv`)

Ogólna tabela zużycia energii — dla przypadków gdy nie wyodrębniamy zakupu, produkcji ani sprzedaży. Zawiera pole `energy_source` (Zakupiona / Wyprodukowana / Sprzedana / Zużyta).

#### 4.1 Zakupiona energia (`tbl_e_purc.csv`)

Energia zakupiona od zewnętrznego dostawcy. Dodatkowe pola: `trader` (nazwa dostawcy), `factor` (wskaźnik dostawcy). Źródła danych: faktury, umowy z dostawcą.

**Wskaźniki dla Polski (KOBiZE 2024):**
- Energia z sieci (nie OZE): **0,709 tCO₂e/MWh**
- Energia z OZE (z certyfikatem GO): **0,000 tCO₂e/MWh**

#### 4.2 Wyprodukowana energia (`tbl_e_prod.csv`)

Energia wytworzona przez własne instalacje (np. farma fotowoltaiczna, turbina wiatrowa, kogeneracja). Dodatkowe pole: `installation` (nazwa instalacji). Źródła: odczyty liczników, raporty OSD.

#### 4.3 Sprzedana energia (`tbl_e_sold.csv`)

Energia odsprzedana innym podmiotom (np. spółkom w grupie na podstawie umowy PPA). Dodatkowe pole: `customer` (odbiorca). Pozwala śledzić przepływy energii wewnątrz grupy kapitałowej.

#### 4.4 Typy energii

Dla wszystkich czterech tabel obowiązują te same typy energii:

| Typ energii | Wskaźnik emisji |
|-------------|-----------------|
| Energia elektryczna nie OZE | 0,709 tCO₂e/MWh (KOBiZE 2024) |
| Energia elektryczna z OZE | 0,000 tCO₂e/MWh |
| Ciepło nie OZE | 0,292 tCO₂e/GJ (KOBiZE 2024) |
| Ciepło z OZE | 0,000 tCO₂e/GJ |
| Para Techniczna nie OZE | 0,292 tCO₂e/GJ |
| Para Techniczna z OZE | 0,000 tCO₂e/GJ |
| Chłód nie OZE | 0,180 tCO₂e/GJ |
| Chłód z OZE | 0,000 tCO₂e/GJ |

### Przykładowe dane w narzędziu:

| Pole | Opis | Przykład |
|------|------|---------|
| Rok | Rok sprawozdawczy | 2025 |
| Firma | Nazwa spółki | GreenTech Polska |
| Ilość | Zużyta ilość | 450 |
| Jednostka | MWh, kWh, GJ, MJ | MWh |
| Typ energii | Rodzaj energii | Energia elektryczna nie OZE |
| Dostawca (zakupiona) | Nazwa dostawcy | PGE Obrót S.A. |
| Instalacja (wyprodukowana) | Nazwa instalacji | Farma PV Wrocław |
| Odbiorca (sprzedana) | Nazwa odbiorcy | GreenTech Polska |
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

### Rejestr zmian (Audit Log)

Narzędzie posiada wbudowany **mechanizm śledzenia zmian** działający analogicznie do triggerów w bazach danych SQL. Każda operacja modyfikująca dane (dodanie, edycja, usunięcie rekordu) w dowolnej tabeli jest automatycznie rejestrowana w dedykowanym logu zmian (`tbl_change_log.csv`).

**Struktura rejestru zmian:**

| Pole | Typ | Opis |
| ---- | --- | ---- |
| `id_rejestr_zmian` | serial | Automatycznie generowany klucz główny |
| `login` | tekst | Login użytkownika, który wykonał zmianę |
| `date_change` | datetime | Data i godzina zmiany (YYYY-MM-DD HH:MM:SS) |
| `table_name` | tekst | Nazwa tabeli, w której nastąpiła zmiana |
| `record_id` | tekst | ID zmienionego rekordu |
| `change_type` | tekst | Typ operacji: INSERT, UPDATE lub DELETE |
| `previous_data` | JSON | Kopia wiersza przed zmianą (null przy INSERT) |
| `actual_data` | JSON | Kopia wiersza po zmianie (null przy DELETE) |

**Zasady działania:**

- **INSERT** — zapisywane jest tylko `actual_data` (nowy rekord, nie było poprzedniego stanu).
- **UPDATE** — zapisywane są oba pola: `previous_data` (stan przed zmianą) i `actual_data` (stan po zmianie).
- **DELETE** — zapisywane jest tylko `previous_data` (usunięty rekord, brak nowego stanu).
- Rejestr zmian jest **niezmienny (immutable)** — nie można edytować ani usuwać wpisów z logu, co zapewnia integralność historii.
- Pola `previous_data` i `actual_data` przechowują dane w formacie **JSON** — przygotowane pod przyszłą migrację na typ JSONB w PostgreSQL.
- Audit log **nie wymaga backupu** — sam jest historią zmian i stanowi dodatkową warstwę zabezpieczenia danych.
- Mechanizm aktywuje się automatycznie po zalogowaniu użytkownika — od tego momentu każda modyfikacja danych jest śledzona.

**Dlaczego to ważne?**

W kontekście raportowania ESG i audytów emisyjnych pełna historia zmian danych jest kluczowa. Audytor może sprawdzić, kto i kiedy modyfikował dane emisyjne, jakie wartości zostały zmienione i czy zmiany były uzasadnione. To element **zasady przejrzystości (Transparency)** z GHG Protocol — łańcuch zmian danych jest udokumentowany i weryfikowalny.

---

## 8. Funkcjonalności i zalety narzędzia

### Główne funkcjonalności

**Zbieranie danych:**
- Interaktywne dodawanie rekordów emisyjnych z walidacją danych wejściowych
- Obsługa wszystkich kategorii Zakresu 1 (spalanie stacjonarne, mobilne, emisje procesowe, fugitive) i Zakresu 2 (zużycie, zakupiona, wyprodukowana i sprzedana energia)
- Interaktywne dodawanie nowych spółek, wskaźników emisji i przeliczników jednostek (tylko admin)
- Automatyczna walidacja typów paliw, jednostek, zakresów dat
- Podgląd szacunkowej emisji już przy wprowadzaniu danych
- **Emisja deklarowana** — użytkownik może podać własną wartość emisji [tCO2eq] z zewnętrznego raportu (np. KOBiZE, DEFRA, pomiar). Jeśli podana — ma priorytet nad obliczeniem automatycznym. Jeśli odchylenie od wskaźnika > ±50% — narzędzie wyświetla ostrzeżenie i prosi o potwierdzenie poprawności danych
- **Pole raport** — źródło raportu emisji (wymagane gdy użytkownik podaje emisję deklarowaną)
- **Pole uwagi (notes)** — dowolne notatki do każdego rekordu emisyjnego

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
- **Eksport do PDF** — profesjonalny raport emisji w formacie PDF z podsumowaniem, tabelami i metodyką. Dostępny z menu raportów

**Zarządzanie danymi:**
- System ról (admin / użytkownik) z kontrolą dostępu na poziomie spółki; admin może dodawać uprawnienia spółek i role użytkowników z poziomu menu
- Walidacja spójności danych (czy firmy w danych emisyjnych istnieją w rejestrze firm)
- Weryfikacja kompletności wskaźników i przeliczników
- **Blokada duplikatów** — próba dodania istniejącej spółki, wskaźnika, przelicznika lub roli użytkownika jest blokowana natychmiast przy wpisywaniu pola (nie dopiero po zatwierdzeniu formularza)
- **Walidacja inline pól spółki** — telefon, e-mail, KRS, REGON i NIP są weryfikowane formatowo przy każdym wpisaniu; błędna wartość wymusza ponowne wpisanie tego samego pola
- Automatyczne kopie zapasowe przy każdej modyfikacji danych
- **Rejestr zmian (audit log)** — automatyczne śledzenie każdej operacji INSERT/UPDATE/DELETE we wszystkich tabelach, z zapisem danych przed i po zmianie w formacie JSON, loginem użytkownika i datą zmiany
- **Hurtowy import danych** — import rekordów emisyjnych z plików CSV lub Excel (.xlsx). Automatyczna walidacja Pydantic, nadawanie ID, raport błędów. Dostępny z menu Narzędzia
- **Poziomy pewności danych (data_quality)** — każdy rekord może mieć oznaczenie jakości danych: *measured* (pomiar), *calculated* (obliczenie), *estimated* (szacunek) — zgodnie z wymogami GHG Protocol

**Komunikacja e-mail:**
- Wysyłanie zapytań do osób odpowiedzialnych za dane emisyjne (osoby z uprawnieniami save + koordynator spółki)
- Automatyczne ustalanie odbiorców na podstawie tbl_authorisations (save=TRUE) i tbl_companies (co_mail)
- 6 szablonów wiadomości: weryfikacja danych, korekta, brakujące dane, wyjaśnienie odchylenia, dane źródłowe (dokumenty), własna wiadomość
- Kontekst rekordu generowany automatycznie: emisja deklarowana vs obliczona, odchylenie %, średnia z lat, porównanie rok do roku
- Wskazywanie konkretnych ID rekordów (kilka na raz, np. 1,5,12) lub całej spółki z wyborem zakresu (Scope 1/2/1+2)
- Podgląd wiadomości przed wysłaniem z potwierdzeniem
- Tryb dry-run (domyślny) ��� zapis do pliku zamiast wysyłania, konfiguracja SMTP w .env
- Rejestr wysłanych wiadomości w tbl_email_log.csv

**Cele redukcji i symulacje:**

- **Cele redukcji (SBTi-style)** — definiowanie celów redukcji emisji: rok bazowy, rok docelowy, % redukcji. Ścieżka redukcji liniowa z wizualizacją postępu rok po roku (rzeczywista emisja vs cel). Obsługuje Scope 1, 2 lub 1+2
- **Symulacje what-if** — interaktywna analiza scenariuszy: co jeśli przejdziemy na OZE? Zmienimy paliwo? Poprawimy efektywność? Scenariusze łączą się kumulatywnie, wynik w porównaniu z aktualnym stanem
- Dostępne strategie symulacji: przejście na OZE (%), poprawa efektywności (%), zmiana paliwa, własna redukcja Scope 1/2 (%)

### Zalety narzędzia

| Cecha | Korzyść |
|-------|---------|
| **Emisja deklarowana z priorytetem** | Własna wartość emisji z raportu ma pierwszeństwo nad obliczeniem automatycznym. Ostrzeżenie przy odchyleniu > ±50% |
| **Obliczenia w pamięci** | Dane źródłowe nie są nadpisywane — zawsze możesz wrócić do oryginału |
| **Automatyczne przeliczanie jednostek** | Nie musisz ręcznie konwertować kWh na MWh czy kg na tony |
| **177 testów automatycznych** | Pewność, że obliczenia są poprawne — każda zmiana kodu jest weryfikowana |
| **Wielospółkowość** | Jedna instalacja obsługuje całą grupę kapitałową |
| **Polskie wskaźniki emisji** | KOBiZE 2024, DEFRA 2024, IPCC AR5 — aktualne i wiarygodne źródła |
| **Kontrola dostępu** | Każdy użytkownik widzi tylko swoje spółki |
| **Audit log (rejestr zmian)** | Pełna historia zmian danych — kto, kiedy i co zmienił. Niezmienny log gotowy na audyt ESG |
| **Eksport CSV i PDF** | Łatwy import do Excela, Power BI + profesjonalny raport PDF gotowy do prezentacji |
| **Hurtowy import CSV/Excel** | Szybkie ładowanie danych z zewnętrznych źródeł (faktur, kart paliwowych) zamiast ręcznego wpisywania |
| **Poziomy pewności danych** | Oznaczenie measured/calculated/estimated — audytor widzi jakość każdego rekordu |
| **Cele redukcji + symulacje** | Ścieżka SBTi z monitoringiem postępu + interaktywne scenariusze what-if (OZE, paliwa, efektywność) |
| **Komunikacja e-mail** | Wysyłanie zapytań do osób odpowiedzialnych za dane — szablony, automatyczny kontekst rekordów, porównanie r/r |
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

### Przypadek 4: Weryfikacja danych emisyjnych e-mailem

Analityk danych zauważa, że spalanie stacjonarne w GreenTech Produkcja wzrosło o 35% r/r. Wchodzi w menu Komunikacja e-mail → Wskaż spółkę → Scope 1 → Spalanie stacjonarne → rok 2025. Narzędzie automatycznie generuje kontekst: emisja bieżąca, rok ubiegły, odchylenie %, średnia z lat. Analityk wybiera szablon „Wyjaśnienie odchylenia", dodaje uwagę i wysyła zapytanie do osób z uprawnieniami save dla tej spółki + koordynatora (co_mail). Mail zawiera konkretne liczby — odbiorca wie, o co dokładnie chodzi.

### Przypadek 5: Prośba o dokumenty źródłowe

Przed audytem ESG analityk potrzebuje faktur potwierdzających zużycie paliwa w rekordach #14, #17 i #22. Wchodzi w Komunikacja e-mail → Wskaż konkretne ID → tabela: spalanie stacjonarne → wpisuje: 14,17,22. Narzędzie sprawdza uprawnienia, wyświetla kontekst każdego rekordu, analityk wybiera szablon „Dane źródłowe" i wysyła. Rejestr wysłanych wiadomości (tbl_email_log.csv) dokumentuje historię komunikacji.

### Przypadek 6: Przejście na OZE

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

### CodeCarbon — jaki ślad węglowy ma samo liczenie śladu węglowego?

**CodeCarbon** to biblioteka Pythona (https://codecarbon.io), która mierzy zużycie energii przez kod i przelicza je na emisje CO₂. Pozwala odpowiedzieć na pytanie: ile kosztuje środowisko uruchomienie naszego kalkulatora?

**Szacunkowa emisja Emission Impossible:**

Typowa sesja z narzędziem (wczytanie danych, obliczenia, generowanie raportów z wykresami) trwa ok. 30-60 sekund aktywnego czasu CPU. Na zwykłym laptopie biurowym (TDP ~15-25 W) wygląda to tak:

| Parametr | Wartość |
|----------|---------|
| Czas CPU sesji | ~30-60 s |
| Moc laptopa (idle + CPU) | ~15-25 W |
| Zużycie energii na sesję | ~0,0002-0,0004 kWh |
| Emisja CO₂ (Polska, 0,709 kg/kWh) | **~0,00015-0,0003 kg CO₂** |
| Emisja CO₂ na sesję | **~0,15-0,3 g CO₂** |

Czyli jedno uruchomienie kalkulatora emituje **mniej niż 1 gram CO₂** — tyle co oddech przez 1 sekundę.

**Porównanie z tradycyjnym podejściem (Excel + e-maile):**

W tradycyjnym procesie raportowania emisji specjalista ESG:
- Zbiera dane z e-maili i faktur — **2-4 godziny** pracy na komputerze
- Ręcznie wpisuje dane do arkusza Excel — **1-2 godziny**
- Sprawdza wskaźniki w dokumentach KOBiZE/DEFRA — **30-60 minut**
- Liczy formuły, weryfikuje, poprawia błędy — **1-2 godziny**
- Wysyła arkusze e-mailem do współpracowników — kolejne wiadomości z załącznikami
- Tworzy wykresy i formatuje raport — **1-2 godziny**

**Łącznie: 6-10 godzin pracy komputerowej na jedno raportowanie.**

| Metoda | Czas pracy | Zużycie energii | Emisja CO₂ (Polska) |
|--------|-----------|-----------------|---------------------|
| **Emission Impossible** | ~1 min | ~0,0003 kWh | **~0,2 g CO₂** |
| **Excel + e-maile** | ~8 h | ~0,12-0,20 kWh | **~85-140 g CO₂** |
| **Stosunek** | **480× szybciej** | **400-600× mniej energii** | **~500× mniej emisji** |

Do tego dochodzą ukryte koszty tradycyjnego podejścia:
- **Serwery pocztowe** — każdy e-mail z załącznikiem Excel to ~4-50 g CO₂ (dane: The Carbon Literacy Project)
- **Przechowywanie w chmurze** — arkusze na OneDrive/Google Drive zużywają energię centrów danych 24/7
- **Powtórzona praca** — błędy w formułach Excel wykrywane po tygodniach wymagają ponownego przeliczenia
- **Wersjonowanie** — „raport_v3_final_FINAL(2).xlsx" to nie tylko żart, ale też zmarnowana energia

**Wniosek:** Automatyzacja obliczeń to nie tylko oszczędność czasu i eliminacja błędów — to realnie niższy ślad węglowy samego procesu raportowania. Narzędzie, które liczy emisje, emituje **500 razy mniej** niż tradycyjna metoda. To jak jazda rowerem do pracy zamiast SUV-em — efekt ten sam, ślad nieporównywalnie mniejszy.

**Jak zmierzyć samodzielnie?** Wystarczy dodać CodeCarbon do projektu:

```python
from codecarbon import EmissionsTracker

tracker = EmissionsTracker(country_iso_code="POL")
tracker.start()
# ... tutaj obliczenia Emission Impossible ...
tracker.stop()
print(f"Emisja sesji: {tracker.final_emissions:.6f} kg CO₂")
```

CodeCarbon zapisze szczegóły do pliku `emissions.csv` — ironicznie, kalkulator emisji generuje własny raport emisyjny.

---

## 12. Instrukcja — Przewodnik po danych emisyjnych

> Ten rozdział służy jako baza do interaktywnego przewodnika w aplikacji — wyjaśnienia wyświetlane użytkownikowi podczas wprowadzania danych.

### Ogólne zasady wprowadzania danych

1. **Rok sprawozdawczy** — rok, w którym nastąpiło zużycie paliwa/energii (nie rok faktury). Jeśli faktura za grudzień 2024 przyszła w styczniu 2025, dane dotyczą roku 2024. **Uwaga:** aplikacja nie pozwala wpisać roku w przyszłości (max = bieżący rok). Dane można raportować najwcześniej od 2010 roku.
2. **Firma** — nazwa spółki prawnej, do której przypisany jest dany koszt/zużycie. W grupie kapitałowej każda spółka raportuje oddzielnie.
3. **Ilość i jednostka** — zawsze podawaj w jednostce z dokumentu źródłowego (faktury). Narzędzie automatycznie przeliczy jeśli potrzeba.
4. **Źródło danych** — podaj skąd pochodzi informacja (faktura, karta paliwowa, odczyt licznika, szacunek). Pomaga to audytorowi zweryfikować dane.
5. **Pewność danych (data_quality)** — oznacz poziom pewności: *measured* (pomiar z faktury/licznika), *calculated* (obliczone z aktywności), *estimated* (szacunek). Pole opcjonalne, ale ważne dla audytu i zgodności z GHG Protocol.

### Spalanie stacjonarne — co wpisać?

| Pytanie | Jak znaleźć odpowiedź |
|---------|----------------------|
| Jaki rodzaj paliwa? | Sprawdź na fakturze — gaz ziemny, olej opałowy, węgiel itp. |
| Ile zużyto? | Ilość z faktury — m³ gazu, tony węgla, litry oleju |
| Jaka instalacja? | Nazwa kotła, pieca, turbiny — pomaga zidentyfikować źródło |
| Emisja [tCO2eq] | Jeśli masz gotową wartość emisji (np. z pomiaru na kominie, raportu KOBiZE) — wpisz ją. Ma priorytet nad obliczeniem automatycznym. Jeśli nie masz — zostaw puste, narzędzie obliczy. |
| Raport | Źródło deklarowanej emisji — np. „KOBiZE", „DEFRA 2024", „pomiar akredytowany". Wymagane gdy podajesz emisję. |
| Uwagi | Opcjonalne notatki — np. „kotłownia budynek B", „szacunek na podstawie Q3". |

### Spalanie mobilne — co wpisać?

| Pytanie | Jak znaleźć odpowiedź |
|---------|----------------------|
| Jaki pojazd? | Typ pojazdu — samochód osobowy, ciężarówka 12t, wózek widłowy |
| Jakie paliwo? | Benzyna, diesel, LPG — z karty paliwowej lub faktury |
| Ile paliwa? | Litry — z karty paliwowej lub faktury za paliwo |
| Emisja [tCO2eq] | Gotowa wartość emisji z raportu — jeśli masz. Priorytet nad obliczeniem. |
| Raport | Źródło deklarowanej emisji — np. „DEFRA 2024", „karta paliwowa z kalkulacją". Wymagane gdy podajesz emisję. |
| Uwagi | Opcjonalne notatki — np. „flota osobowa", „pojazdy budowlane". |

**Wskazówka:** Jeśli nie masz danych o zużyciu paliwa, ale masz przejechane kilometry, skontaktuj się z działem floty — przebiegi można przeliczyć na litry paliwa.

### Emisje procesowe — co wpisać?

| Pytanie | Jak znaleźć odpowiedź |
|---------|----------------------|
| Jaki proces? | Nazwa procesu technologicznego — kalcynacja, synteza, topienie |
| Jaki produkt? | Co jest wytwarzane — wapno, kwas, metal |
| Ile przetworzone? | Tony surowca/produktu — z raportów produkcyjnych |
| Emisja [tCO2eq] | Gotowa wartość emisji z raportu zakładowego. Priorytet nad obliczeniem. |
| Raport | Źródło deklarowanej emisji — np. „raport środowiskowy 2024", „KOBiZE". Wymagane gdy podajesz emisję. |
| Uwagi | Opcjonalne notatki — np. „linia produkcyjna nr 2", „piec obrotowy". |

### Emisje niezorganizowane — co wpisać?

| Pytanie | Jak znaleźć odpowiedź |
|---------|----------------------|
| Jaka instalacja? | Nazwa systemu — klimatyzacja biuro, chłodnia magazyn |
| Jaki czynnik? | Typ czynnika chłodniczego — R410A, R32, R404A — z karty serwisowej |
| Ile wyciekło? | Ilość uzupełnionego czynnika (kg) = ilość wycieku — z protokołu serwisu |
| Emisja [tCO2eq] | Gotowa wartość emisji — jeśli serwisant podał w protokole. Priorytet nad obliczeniem z GWP. |
| Raport | Źródło deklarowanej emisji — np. „protokół serwisu klima", „F-gaz raport". Wymagane gdy podajesz emisję. |
| Uwagi | Opcjonalne notatki — np. „klimatyzacja piętro 3", „wymiana sprężarki". |

**Ważne:** Jeśli nie było serwisu i uzupełnienia czynnika w danym roku — emisja fugitive = 0 dla tej instalacji.

### Zużycie energii (Scope 2) — co wpisać?

| Pytanie | Jak znaleźć odpowiedź |
|---------|----------------------|
| Źródło energii | Zakupiona (z sieci), Wyprodukowana (własna PV), Sprzedana |
| Typ energii | Energia elektryczna (OZE/nie OZE), ciepło, para, chłód |
| Ile? | MWh lub GJ — z faktury od dostawcy energii |
| OZE czy nie? | Sprawdź umowę z dostawcą — czy masz certyfikat Gwarancji Pochodzenia (GO)? Jeśli tak → OZE (emisja = 0). Jeśli nie → nie OZE. |
| Emisja [tCO2eq] | Scope 2 jest zawsze obliczane automatycznie ze wskaźnika — to pole jest informacyjne. |
| Uwagi | Opcjonalne notatki — np. „umowa PPA z farmą wiatrową", „certyfikat GO nr 12345". |

**Ważna uwaga o OZE:** Sam fakt, że dostawca „oferuje zieloną energię" nie wystarczy. Liczy się certyfikat Gwarancji Pochodzenia (GO) — formalny dokument potwierdzający, że konkretna ilość energii pochodzi ze źródła odnawialnego. Bez GO, nawet jeśli dostawca reklamuje się jako „zielony", energia powinna być raportowana jako nie-OZE.

### Wskaźniki emisji — jak dodawać i aktualizować?

Wskaźnik emisji (`tbl_factors.csv`) jest unikalny po kombinacji `(nazwa, kraj, rok)`. Oznacza to, że ten sam wskaźnik (np. „Energia elektryczna", Polska) może mieć różne wartości dla różnych lat — co pozwala śledzić zmianę wskaźnika KOBiZE rok do roku.

| Pole | Opis | Przykład |
| ---- | ---- | -------- |
| Nazwa wskaźnika | Musi dokładnie odpowiadać nazwie paliwa lub typu energii | `Energia elektryczna nie OZE` |
| Kraj | Kraj dla którego obowiązuje wskaźnik | `Polska` |
| Rok | Rok obowiązywania (unikalność!) | `2025` |
| Wartość | Liczba dziesiętna ≥ 0 | `0.709` |
| Jednostka | Format: wynik/wejście | `tCO2e/MWh` |
| Źródło | Publikacja (opcjonalne) | `KOBiZE 2025` |

Przy wyszukiwaniu wskaźnika do obliczeń (`get_factor`) — system dobiera wskaźnik **dla roku rekordu emisyjnego**. Jeśli rekord dotyczy roku 2024, szukany jest wskaźnik z kolumną `rok=2024`. Jeśli brak wskaźnika dla tego roku — fallback na najnowszy dostępny rok. Ta logika obowiązuje we wszystkich ścieżkach obliczeniowych: Scope 1, Scope 2, podgląd emisji przy dodawaniu rekordu, walidacja plików, generowanie podsumowań i wysyłka e-mail.

### Przeliczniki jednostek — jak dodawać?

Przelicznik (`tbl_converters.csv`) jest unikalny po parze `(unit_from, unit_to)`. Przelicznik odwrotny jest wyliczany automatycznie — nie trzeba dodawać obu kierunków.

| Pole | Opis | Przykład |
| ---- | ---- | -------- |
| Jednostka źródłowa | Jednostka przed przeliczeniem | `MWh` |
| Jednostka docelowa | Jednostka po przeliczeniu | `GJ` |
| Mnożnik | `unit_from × mnożnik = unit_to` | `3.6` |

### Pewność danych (data_quality) — jak oceniać jakość źródeł?

GHG Protocol wymaga, aby organizacja określiła jakość danych wykorzystanych do obliczeń emisji. Każdy rekord emisyjny w narzędziu ma pole **data_quality**, które przyjmuje jedną z trzech wartości:

| Poziom | Opis | Przykłady | Wiarygodność |
|--------|------|-----------|-------------|
| **measured** | Dane zmierzone — pochodzą z dokumentu źródłowego | Faktura za gaz (10 000 m³), odczyt licznika energii, protokół serwisu klimatyzacji, karta paliwowa | Najwyższa — bezpośredni pomiar |
| **calculated** | Dane obliczone — wyliczone z innej mierzalnej wielkości | Przebiegi km przeliczone na litry paliwa, zużycie energii oszacowane z mocy i godzin pracy urządzeń | Średnia — zależy od jakości założeń |
| **estimated** | Dane szacunkowe — brak dokumentu źródłowego | „Zużywamy ok. 5 ton węgla rocznie", ekstrapolacja z jednego miesiąca na rok, dane branżowe uśrednione | Najniższa — wymaga weryfikacji |

**Jak korzystać:**

1. Przy dodawaniu każdego rekordu emisyjnego narzędzie pyta o pewność danych
2. Pole jest opcjonalne — ale jego brak oznacza, że audytor nie wie, ile wart jest dany rekord
3. Dążyć do maksymalizacji rekordów z poziomem **measured** — to fundament wiarygodnego raportu

**Jak poprawić jakość danych:**

| Obecny poziom | Co zrobić, aby podnieść |
|---------------|------------------------|
| estimated → calculated | Znajdź dane pośrednie: jeśli nie masz faktur za paliwo, sprawdź przebiegi floty i średnie spalanie |
| estimated → measured | Poproś księgowość o oryginały faktur, dział techniczny o odczyty liczników |
| calculated → measured | Zainstaluj podliczniki energii, wprowadź karty paliwowe, zbieraj protokoły serwisowe |

**Dlaczego to ważne:**

- Audytor ESG ocenia nie tylko wynik (ile tCO₂e) ale też **jak** go policzono
- Raport CSRD wymaga ujawnienia poziomu niepewności danych
- Rekordy *estimated* mogą wymagać dodatkowego uzasadnienia lub zastrzeżenia w raporcie
- Im więcej *measured*, tym większa wiarygodność raportu — i tym mniejsze ryzyko przy audycie

### Cele redukcji emisji — jak wyznaczać i monitorować?

Narzędzie pozwala definiować cele redukcji emisji wzorowane na metodologii **SBTi** (Science Based Targets initiative) i monitorować postęp ich realizacji rok po roku.

#### Czym jest cel redukcji?

Cel redukcji to zobowiązanie do zmniejszenia emisji o określony procent w określonym czasie, np.:
- *„Zmniejszyć emisje Scope 1+2 o 42% do 2030 roku (vs 2023)"* — zgodne ze ścieżką SBTi 1.5°C
- *„Osiągnąć neutralność Scope 2 do 2028"* — pełne przejście na OZE
- *„Zredukować Scope 1 o 30% do 2027"* — np. wymiana floty na hybrydy

#### Jak dodać cel?

Menu: **Cele i symulacje → Dodaj cel redukcji**

| Pytanie | Co wpisać |
|---------|-----------|
| Firma | Spółka, dla której definiujesz cel |
| Nazwa celu | Np. „SBTi 1.5°C", „Strategia dekarbonizacji 2030", „Carbon neutral 2028" |
| Rok bazowy | Rok odniesienia — od niego liczymy redukcję. Najczęściej ostatni pełny rok z danymi |
| Rok docelowy | Do kiedy cel ma być osiągnięty |
| Redukcja (%) | O ile procent zmniejszyć emisję vs rok bazowy (np. 42 = spadek o 42%) |
| Zakres | Scope 1, Scope 2 lub 1+2 — które emisje obejmuje cel |

#### Jak działa ścieżka redukcji?

Narzędzie dzieli cel **liniowo** na poszczególne lata. Przykład:

- Emisja bazowa (2023): **530 tCO₂e**
- Cel: **-42% do 2030** (7 lat)
- Roczna redukcja: ~6%/rok = ~31.8 tCO₂e/rok

```text
Rok     Cel [tCO2e]   Rzeczywista    Status
2023        530.000       530.000     ✓ na torze
2024        498.000       496.000     ✓ na torze
2025        466.000       479.000     ✗ powyżej (+2.7%)
2026        434.000           —       (przyszłość)
...
2030        307.000           —       (cel końcowy)
```

- **✓ na torze** — rzeczywista emisja ≤ cel na dany rok
- **✗ powyżej** — przekroczenie celu z podanym % odchylenia
- **(przyszłość)** — lata bez danych (jeszcze nie nadeszły)

#### Typowe cele (inspiracja)

| Typ celu | Redukcja | Horyzont | Dla kogo |
|----------|----------|----------|----------|
| SBTi 1.5°C | -42% Scope 1+2 | 5-10 lat | Firmy dążące do najambitniejszego celu klimatycznego |
| SBTi well-below 2°C | -25% Scope 1+2 | 5-10 lat | Firmy z przemysłu ciężkiego, gdzie szybsza redukcja jest trudna |
| Neutralność Scope 2 | -100% Scope 2 | 3-5 lat | Firmy planujące pełne przejście na OZE |
| Redukcja floty | -30% Scope 1 | 3-5 lat | Firmy z dużą flotą pojazdów (logistyka, dystrybucja) |

### Symulacje what-if — planowanie działań redukcyjnych

Symulacje pozwalają odpowiedzieć na pytanie: **„Co się stanie z naszymi emisjami, jeśli...?"** — bez zmiany rzeczywistych danych.

#### Jak uruchomić symulację?

Menu: **Cele i symulacje → Symulacja what-if**

1. Wybierz firmę i rok do analizy
2. Dodawaj scenariusze jeden po drugim (można łączyć kilka)
3. Wpisz **ok** aby obliczyć wynik
4. Narzędzie pokaże porównanie: obecna emisja vs po zastosowaniu scenariuszy

#### Dostępne scenariusze

| Scenariusz | Co robi | Przykład użycia |
|------------|---------|-----------------|
| **Przejście na OZE** | Zamienia X% energii nie-OZE na OZE → Scope 2 spada | „Co jeśli 50% energii z certyfikatem GO?" |
| **Poprawa efektywności** | Zmniejsza zużycie o X% → Scope 1 i 2 spadają | „Co jeśli zmodernizujemy kotłownię o 15%?" |
| **Zmiana paliwa** | Zamienia paliwo A na B → Scope 1 się zmienia | „Co jeśli wymienimy węgiel na gaz ziemny?" |
| **Własna redukcja** | Bezpośrednio podajesz % redukcji Scope 1 i Scope 2 | „Co jeśli Scope 1 -20%, Scope 2 -50%?" |

#### Przykład wyniku symulacji

Scenariusz: *50% energii na OZE + 15% poprawa efektywności*

```
Kategoria                        Obecna      Symulacja
Scope 1 — stacjonarne             43.430        36.916
Scope 1 — mobilne                 31.452        26.734
Scope 1 — niezorganizowane         3.046         2.589
Scope 2 — energia                400.810       170.344
────────────────────────────────────────────────────────
ŁĄCZNIE                          478.738       236.583

Oszczędność: 242.155 tCO2e (50.6%)
```

#### Jak wykorzystać symulacje w praktyce?

1. **Porównaj z celem** — jeśli cel to -42% a symulacja daje -50%, plan jest wystarczający
2. **Optymalizuj koszty** — porównaj kilka scenariuszy i wybierz najtańszy do wdrożenia
3. **Raportuj zarządowi** — symulacja pokazuje konkretne liczby, nie ogólne obietnice
4. **Iteruj** — łącz scenariusze: najpierw OZE, potem efektywność, potem zmiana paliwa — i sprawdź łączny efekt

#### Ograniczenia symulacji

- Symulacja operuje na **danych z wybranego roku** — nie przewiduje przyszłych zmian
- Ścieżka redukcji jest **liniowa** — w rzeczywistości redukcja bywa nierównomierna
- Scenariusz „zmiana paliwa" przelicza emisję proporcjonalnie do wskaźników — nie uwzględnia różnic w sprawnościach instalacji
- Symulacja nie zmienia danych w CSV — to narzędzie analityczne, nie edycyjne

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
| **Audit log** | Rejestr zmian — automatyczny zapis każdej modyfikacji danych (jak trigger SQL) |
| **Data quality** | Poziom pewności danych: measured (pomiar), calculated (obliczenie), estimated (szacunek) |
| **What-if** | Symulacja hipotetyczna — analiza wpływu planowanych działań na emisje bez zmiany danych |
| **Redukcja liniowa** | Ścieżka redukcji zakładająca stałą kwotę zmniejszenia emisji w każdym roku |
| **Dry-run** | Tryb testowy wysyłki e-mail — wiadomość zapisywana do pliku zamiast wysyłana przez SMTP |

---

## 13. Komunikacja e-mail — zapytania o dane

### Po co?

W procesie weryfikacji danych emisyjnych analityk musi komunikować się z osobami odpowiedzialnymi za dane w poszczególnych spółkach — pytać o poprawność, prosić o korekty, wyjaśniać odchylenia, żądać dokumentów źródłowych. Moduł e-mail automatyzuje tę komunikację bezpośrednio z poziomu narzędzia.

### Jak działa?

Menu: **Menu główne → Komunikacja e-mail**

#### Opcja 1: Wskaż spółkę (zakres/tabela)

Służy do zapytań o dane zbiorcze — emisje całej spółki lub wybranej kategorii.

1. Wybierz spółkę
2. Wybierz zakres:
   - **Scope 1** → podmenu: spalanie stacjonarne, mobilne, niezorganizowane, procesowe lub cały Scope 1
   - **Scope 2** → energia (całość)
   - **Scope 1+2** → całkowity ślad węglowy
3. Wybierz rok — narzędzie automatycznie porównuje z rokiem n-1
4. Narzędzie wyświetla kontekst: emisja bieżąca, emisja rok wcześniej, zmiana r/r (%), średnia z lat, rozkład kategorii
5. Wybierz szablon wiadomości
6. Dodaj opcjonalną uwagę
7. Podgląd wiadomości → potwierdzenie → wysyłka

**Odbiorcy ustalani automatycznie:** wszyscy użytkownicy z uprawnieniami save=TRUE dla danej spółki (login → e-mail z tbl_users) + adres koordynatora spółki (co_mail z tbl_companies).

#### Opcja 2: Wskaż konkretne ID rekordów

Służy do zapytań o konkretne rekordy — np. podejrzane wartości, brakujące dokumenty.

1. Wybierz tabelę (spalanie stacjonarne, mobilne, niezorganizowane, procesowe, zużycie energii)
2. Wpisz ID rekordów oddzielone przecinkiem (np. `14,17,22`)
3. Narzędzie sprawdza uprawnienia użytkownika do spółek tych rekordów
4. Wyświetla kontekst każdego rekordu osobno:
   - Dane rekordu (spółka, rok, paliwo/energia, ilość, jednostka)
   - Emisja deklarowana vs obliczona + odchylenie %
   - Średnia emisji z wszystkich lat
   - Porównanie do roku n-1
5. Wybierz szablon → uwaga → podgląd → wyślij

**Ważne:** Wszystkie wskazane ID muszą być z tej samej tabeli. Rekordy mogą być z różnych lat i różnych spółek — odbiorcy dobierani automatycznie dla każdej spółki.

#### Opcja 3: Historia wysłanych wiadomości

Wyświetla ostatnie 20 wiadomości wysłanych przez zalogowanego użytkownika. Admin widzi wiadomości wszystkich użytkowników.

### Szablony wiadomości

| Szablon | Kiedy używać | Przykład |
|---------|-------------|---------|
| **Weryfikacja danych** | Rutynowa prośba o potwierdzenie poprawności | „Proszę potwierdzić dane za 2025 rok" |
| **Korekta danych** | Wykryto błąd wymagający poprawy | „Ilość diesel w rekordzie #14 wydaje się zawyżona" |
| **Brakujące dane** | Brak danych w porównaniu do roku ubiegłego | „W 2025 brak danych o spalaniu mobilnym (było w 2024)" |
| **Wyjaśnienie odchylenia** | Duża zmiana emisji/zużycia r/r | „Spalanie stacjonarne wzrosło o 35% — proszę o wyjaśnienie" |
| **Dane źródłowe** | Audyt — potrzebne dokumenty | „Proszę o faktury/protokoły dla rekordów #14, #17, #22" |
| **Własna wiadomość** | Nietypowe pytanie | Dowolna treść z kontekstem danych |

### Konfiguracja

W pliku `.env`:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=twoj.email@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
SMTP_FROM_NAME=Imię Nazwisko — Analityk danych
EMAIL_DRY_RUN=true
```

- **EMAIL_DRY_RUN=true** (domyślnie) — wiadomości zapisywane do pliku w `data_files/export/` zamiast wysyłane. Idealne do testowania
- **EMAIL_DRY_RUN=false** — prawdziwa wysyłka przez SMTP

Dla Gmaila wymagane jest „Hasło do aplikacji" (App Password) — nie hasło do konta Google.

### Rejestr wysłanych wiadomości

Każda wysłana wiadomość (również w trybie dry-run) jest logowana w `data_files/tbl_email_log.csv`:

| Pole | Opis |
|------|------|
| id | Unikalny ID wiadomości |
| date | Data i godzina wysłania |
| sender | Login nadawcy |
| recipients | Adresy e-mail odbiorców (rozdzielone ;) |
| company | Spółka której dotyczy |
| table_name | Tabela (jeśli dotyczy konkretnej) |
| record_ids | ID rekordów (rozdzielone ,) |
| template_type | Typ szablonu |
| subject | Temat wiadomości |
| scope | Zakres (1, 2, 1+2) |
| year | Rok którego dotyczy |

Rejestr jest niezmienny (immutable) — jak audit log. Stanowi dokumentację komunikacji z osobami odpowiedzialnymi za dane, przydatną przy audycie ESG.

---

*Dokument przygotowany na potrzeby prezentacji narzędzia Emission Impossible.*
*Metodologia zgodna z GHG Protocol Corporate Standard (Revised Edition).*
*Wskaźniki emisji: KOBiZE 2024, DEFRA 2024, IPCC AR5.*
