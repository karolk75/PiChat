# PiChat: Asystent AI z Raspberry Pi i Azure

## Spis treści

1. [Przegląd projektu](#przegląd-projektu)
2. [Architektura systemu](#architektura-systemu)
3. [User Stories](#user-stories)
4. [Interfejs webowy](#interfejs-webowy)
5. [Interfejs głosowy](#interfejs-głosowy)
6. [Wymagania sprzętowe](#wymagania-sprzętowe)
7. [Wymagania programowe](#wymagania-programowe)
8. [Opcje personalizacji](#opcje-personalizacji)
9. [Synchronizacja w czasie rzeczywistym](#synchronizacja-w-czasie-rzeczywistym)
10. [Dokumentacja REST API](#dokumentacja-rest-api)
11. [Kolekcja Postmana do przetestowania](#kolekcja-postmana-do-przetestowania)
12. [Kalkulator kosztów](#kalkulator-kosztów)
13. [Podsumowanie](#podsumowanie)

## Przegląd projektu

PiChat to wszechstronny system chatbota AI, który łączy moc Raspberry Pi z usługami chmurowymi Azure, tworząc asystenta z podwójnym interfejsem. System oferuje:

1. **Interfejs głosowy**: Użyj fizycznego przycisku na Raspberry Pi, aby aktywować tryb głosowy, umożliwiający naturalną rozmowę z asystentem AI.
2. **Interfejs webowy**: Dostęp do tych samych możliwości AI poprzez responsywną aplikację webową, zapewniającą rozmowy tekstowe i zarządzanie historią.

System obsługuje wiele modeli językowych, umożliwia personalizację osobowości asystenta oraz zachowuje historię rozmów w obu interfejsach. Wszystkie interakcje użytkownika są przechowywane w bazie danych, co umożliwia przeglądanie i kontynuowanie poprzednich rozmów.

## Architektura systemu

### Kontekst systemu (C1)

![Diagram kontekstu systemu PiChat](PiChat_diagram_c1.png)

System PiChat umożliwia interakcję użytkownika z asystentem AI poprzez interfejs głosowy (Raspberry Pi) oraz interfejs webowy. System wykorzystuje usługi chmurowe Azure do przetwarzania języka naturalnego, przechowywania danych i hostowania aplikacji webowej.

### Kontenery (C2)

![Diagram kontenerów systemu PiChat](PiChat_diagram_c2.png)

Diagram pokazuje główne komponenty systemu PiChat:
- Interfejs głosowy oparty o Raspberry Pi obsługujący interakcje głosowe
- Aplikacja webowa oferująca interfejs tekstowy
- Backend Websocket hostowany na Azure App Service, obsługujący WebSockety dla bezpośredniej komunikacji w czasie rzeczywistym bez pośredników
- Azure SQL Database do przechowywania danych aplikacji
- Azure OpenAI Service do przetwarzania języka naturalnego
- Azure Speech Service do konwesacji głosu na tekst i testu na głos

## User Stories

### Podstawowe funkcjonalności

**Jako użytkownik Raspberry Pi, chcę:**
1. Aktywować asystenta poprzez naciśnięcie przycisku, aby rozpocząć rozmowę głosową
2. Zadawać pytania ustnie i słyszeć odpowiedzi głosowe, aby wygodnie uzyskiwać informacje
3. Kontynuować poprzednie rozmowy głosowe, aby nie tracić kontekstu dyskusji
4. Mieć możliwość przerwania odpowiedzi asystenta, aby zadać nowe pytanie

**Jako użytkownik aplikacji webowej, chcę:**
1. Utworzyć nową rozmowę tekstową z asystentem, aby rozpocząć nowy temat
2. Przeglądać historię moich poprzednich rozmów, aby wrócić do udzielonych wcześniej informacji
3. Kontynuować dowolną wcześniejszą rozmowę, aby rozwinąć temat
4. Usuwać wybrane rozmowy, które nie są już potrzebne
5. Zmienić nazwę rozmowy, aby łatwiej ją odnaleźć

### Zaawansowane funkcjonalności

**Jako użytkownik zaawansowany, chcę:**
1. Przełączać się między różnymi modelami AI (GPT-4, GPT-3.5), aby dostosować jakość i koszt odpowiedzi
2. Dostosować ustawienia głosu asystenta (płeć, akcent), aby personalizować doświadczenie
3. Eksportować historię rozmów do pliku, aby zachować ważne informacje
4. Dostosować osobowość asystenta, aby lepiej odpowiadał moim preferencjom
5. Otrzymywać powiadomienia o aktualizacjach systemu

## Interfejs webowy

Interfejs webowy PiChat to aplikacja oferująca wygodny dostęp do asystenta AI poprzez przeglądarkę internetową. 

### Funkcje interfejsu webowego

#### Panel rozmów
- Lista wszystkich rozmów użytkownika
- Opcje filtrowania i wyszukiwania rozmów
- Przycisk tworzenia nowej rozmowy
- Wskaźnik aktywnej rozmowy
- Opcje zarządzania rozmowami (zmiana nazwy, usunięcie)

#### Okno czatu
- Historia wiadomości z oznaczeniem ról (użytkownik/asystent)
- Pole wprowadzania nowej wiadomości
- Przyciski funkcyjne (wysłanie, anulowanie pisania, dodanie załącznika)
- Wskaźnik pisania asystenta
- Opcje formatowania tekstu (markdown)

#### Panel ustawień
- Wybór modelu AI (GPT-4, GPT-3.5)
- Parametry głosu asystenta
- Osobowość asystenta
- Preferencje powiadomień
- Opcje prywatności i przechowywania danych

### Technologie interfejsu webowego
- React.js dla interaktywnych komponentów UI
- Redux do zarządzania stanem aplikacji
- TailwindCSS dla stylizacji
- Natywne WebSockety (WebSocket API) dla komunikacji w czasie rzeczywistym

## Interfejs głosowy

Interfejs głosowy PiChat działa na Raspberry Pi, oferując naturalne interakcje głosowe z asystentem AI.

### Komponenty fizyczne
- **Przycisk aktywacyjny**: Fizyczny przycisk podłączony do GPIO Raspberry Pi
- **Pierścień LED**: Wskaźnik wizualny stanu systemu
- **Mikrofon**: Mikrofon wysokiej jakości z redukcją szumów
- **Głośnik**: Mini głośnik do odtwarzania odpowiedzi

### Stany interfejsu głosowego
1. **Stan spoczynku**: System oczekuje na aktywację
2. **Nasłuchiwanie**: System aktywuje mikrofon po naciśnięciu przycisku
3. **Przetwarzanie**: System analizuje zapytanie
4. **Odpowiadanie**: Asystent udziela odpowiedzi głosowej
5. **Stan błędu**: Sygnalizacja problemu

### Interakcje głosowe
- **Aktywacja**: Naciśnięcie przycisku lub fraza aktywacyjna
- **Przerwanie**: Ponowne naciśnięcie przycisku podczas odpowiedzi
- **Kontynuacja**: Automatyczne nasłuchiwanie po zakończeniu odpowiedzi
- **Zakończenie**: Przejście w stan spoczynku po bezczynności

### Implementacja klienta Raspberry Pi
- **Aplikacja kliencka**: Program w Python 3 działający jako usługa systemowa
- **Biblioteki komunikacyjne**: 
  - `websockets` dla komunikacji w czasie rzeczywistym przez WebSockety
  - `requests` do komunikacji REST API
- **Proces autoryzacji**: Prosty token API generowany przy pierwszej konfiguracji
- **Przetwarzanie offline**: Podstawowe funkcje działają również przy braku połączenia
- **Automatyczny restart**: Auto-odnowienie połączenia przy utracie komunikacji

## Wymagania sprzętowe

### Komponenty podstawowe

| Komponent | Minimalne wymagania | Zalecane specyfikacje |
|-----------|---------------------|------------------------|
| Komputer jednopłytkowy | Raspberry Pi 4 Model B (1GB) | Raspberry Pi 4 Model B (2GB+) |
| Karta microSD | 16GB, Class 10 | 32GB+, UHS Speed Class 3 |
| Zasilacz | 5V/2.5A | 5V/3A, USB-C |
| Obudowa | Podstawowa | Z pasywnym chłodzeniem |

### Komponenty audio

| Komponent | Minimalne wymagania | Zalecane specyfikacje |
|-----------|---------------------|------------------------|
| Mikrofon | USB, jednokierunkowy | USB z redukcją szumów |
| Głośnik | Mini głośnik USB | Głośnik I2S z wzmacniaczem |
| Karta dźwiękowa | Wbudowana | USB DAC |

### Komponenty dodatkowe

| Komponent | Minimalne wymagania | Zalecane specyfikacje |
|-----------|---------------------|------------------------|
| Przycisk fizyczny | Przycisk taktowy | Przycisk z podświetleniem |
| Diody LED | Pojedyncza dioda | Pierścień Neopixel (WS2812) |
| Połączenie sieciowe | Wi-Fi | Ethernet + Wi-Fi |
| Zasilanie awaryjne | Brak | UPS HAT lub powerbank |

## Wymagania programowe

### System operacyjny
- Raspberry Pi OS (Debian Bullseye) 32/64-bit
- Jądro 5.10+
- Odpowiednie uprawnienia do zasobów systemowych

### Oprogramowanie serwerowe
- Python 3.11+
- FastAPI 0.110+
- Uvicorn 0.27+
- SQLAlchemy 2.0+
- NGINX 1.18+ (dla środowiska produkcyjnego)
- Docker (opcjonalnie) 20+

### Usługi chmurowe Azure
- Azure Speech Services
- Azure OpenAI Service
- Azure App Service (dla hostowania backendu REST API)
- Azure Blob Storage
- Azure SQL Database

## Opcje personalizacji

System PiChat oferuje szerokie możliwości personalizacji, pozwalając na dostosowanie asystenta AI do indywidualnych potrzeb i preferencji.

### Personalizacja asystenta AI

#### Modele językowe
- **GPT-4**: Najnowszy model z najwyższą jakością odpowiedzi (Azure OpenAI GPT-4)
- **GPT-3.5-Turbo**: Szybki model o dobrej jakości odpowiedzi i niższym koszcie (Azure OpenAI GPT-3.5)

#### Osobowość asystenta
- **Pomocny**: Standardowy, przyjazny asystent
- **Profesjonalny**: Formalny ton, konkretne odpowiedzi
- **Przyjacielski**: Ciepły, konwersacyjny styl
- **Zwięzły**: Krótkie, bezpośrednie odpowiedzi
- **Edukacyjny**: Szczegółowe wyjaśnienia z elementami dydaktycznymi

### Personalizacja interfejsu głosowego

#### Głosy asystenta
- Wybór płci głosu (męski, żeński, neutralny)
- Wybór akcentu (polski, angielski)
- Regulacja tempa mowy
- Regulacja wysokości głosu

#### Ustawienia nasłuchiwania
- Czas nasłuchiwania po aktywacji
- Czułość wykrywania ciszy
- Słowo aktywacyjne (alternatywa dla przycisku)
- Rozpoznawanie konkretnych użytkowników

## Synchronizacja w czasie rzeczywistym

System PiChat zapewnia pełną synchronizację w czasie rzeczywistym między interfejsem głosowym (Raspberry Pi) a interfejsem webowym, wykorzystując natywne protokoły WebSocket obsługiwane bezpośrednio przez Azure App Service, co upraszcza architekturę dla osobistego użytku.

### Architektura komunikacji w czasie rzeczywistym

- **Backend (Azure App Service)** - obsługuje WebSockety bezpośrednio, bez dodatkowych usług pośredniczących
- **Interfejs webowy** - używa natywnego WebSocket API do komunikacji w czasie rzeczywistym
- **Raspberry Pi** - działa jako klient WebSocket, łączący się z backendem za pomocą biblioteki websockets dla Python

### Proces autoryzacji i uwierzytelniania

1. **Autoryzacja**:
   - Prosta autoryzacja przez token API (dla osobistego użytku)
   - Brak potrzeby skomplikowanej infrastruktury uwierzytelniania dla jednego użytkownika
   - Możliwość zabezpieczenia hasłem lub prostym tokenem

### Przepływ informacji w czasie rzeczywistym

1. **Inicjalizacja połączenia**:
   - Interfejs webowy i Raspberry Pi nawiązują bezpośrednie połączenie WebSocket z serwerem
   - Prosty proces uwierzytelniania przy połączeniu

2. **Synchronizacja rozmów głosowych**:
   - Zapytanie głosowe jest przetwarzane na tekst i wysyłane do backendu przez API REST
   - Backend przesyła wiadomość przez WebSockety do połączonych klientów
   - Interfejs webowy wyświetla pytanie użytkownika w czasie rzeczywistym
   - Odpowiedź asystenta jest generowana i transmitowana jako strumień przez WebSockety
   - Raspberry Pi przetwarza odpowiedź tekstową na mowę

3. **Synchronizacja rozmów webowych**:
   - Wiadomości wysłane przez interfejs webowy są publikowane przez WebSockety
   - Raspberry Pi może odtworzyć odpowiedź głosową (opcjonalnie)

### Obsługa strumieniowania odpowiedzi

- Odpowiedzi asystenta AI są strumieniowane w czasie rzeczywistym do klientów
- Implementacja wykorzystuje natywny protokół WebSocket
- Dla prostego przypadku użycia, strumieniowanie odbywa się bez dodatkowej infrastruktury

## Dokumentacja REST API

REST API jest centralnym elementem systemu PiChat, umożliwiającym komunikację między interfejsami użytkownika a usługami chmurowymi. API jest hostowane na Azure App Service i oferuje następujące grupy endpointów:

### Infrastruktura API
- **Hosting**: Azure App Service z obsługą WebSockets
- **Autoryzacja**: JWT z Azure AD B2C
- **Dokumentacja**: Swagger/OpenAPI 3.0
- **Rate limiting**: Wbudowane limity zapytań dla ochrony zasobów

### Grupy endpointów

#### Zarządzanie rozmowami
- `GET /api/conversations` - Pobieranie listy rozmów
- `POST /api/conversations` - Tworzenie nowej rozmowy
- `GET /api/conversations/{id}` - Pobieranie szczegółów rozmowy
- `PUT /api/conversations/{id}` - Aktualizacja tytułu rozmowy
- `DELETE /api/conversations/{id}` - Usuwanie rozmowy

#### Wiadomości
- `POST /api/conversations/{id}/messages` - Wysyłanie nowej wiadomości
- `GET /api/conversations/{id}/messages/stream` - Strumieniowanie odpowiedzi asystenta

#### WebSocket
- `GET /api/ws` - Endpoint WebSocket do komunikacji w czasie rzeczywistym
- `GET /api/ws/info` - Informacje o statusie połączeń WebSocket

#### Ustawienia i głos
- `GET /api/settings` - Pobieranie ustawień użytkownika
- `PUT /api/settings` - Aktualizacja ustawień użytkownika
- `POST /api/speech/text-to-speech` - Konwersja tekstu na mowę
- `POST /api/speech/speech-to-text` - Konwersja mowy na tekst

## Kolekcja Postmana do przetestowania

Dla ułatwienia testowania API, przygotowana została kolekcja Postmana zawierająca wszystkie endpointy wraz z przykładowymi zapytaniami. Kolekcja obejmuje:

1. Środowiska dla różnych etapów (deweloperskie, testowe, produkcyjne)
2. Predefiniowane zmienne dla adresów URL, tokenów i identyfikatorów
3. Przykłady zapytań dla wszystkich endpointów
4. Testy automatycznie sprawdzające poprawność odpowiedzi

## Kalkulator kosztów

Poniżej przedstawiam szacowane koszty miesięczne dla rozwiązania PiChat:

### Koszt usług Azure (miesięcznie)

| Usługa | Specyfikacja | Użycie | Koszt (EUR) |
|--------|-------------|--------|------------|
| Azure Speech Services | Standard | 5 godz. rozpoznawania/syntezy mowy dziennie | 4.20 € |
| Azure OpenAI Service | GPT-4 | 100 zapytań dziennie | 7.50 € |
| Azure App Service | B1 Basic | Hostowanie aplikacji webowej i REST API 24/7 | 12.41 € |
| Azure Blob Storage | Hot tier | 5 GB danych | 0.10 € |
| Azure SQL Database | Basic tier | 2 GB danych | 4.21 € |
| Azure Bandwidth | | 10 GB wyjściowe | 0.81 € |
| **SUMA** | | | **29.23 €** |

### Sprzęt jednorazowy

| Komponent | Koszt (EUR) |
|-----------|-------------|
| Raspberry Pi 4 (2GB) | 45.00 € |
| Karta microSD (32GB) | 10.00 € |
| Mikrofon USB | 15.00 € |
| Głośnik + wzmacniacz I2S | 12.00 € |
| Przycisk i komponenty | 3.00 € |
| Obudowa drukowana 3D | 5.00 € |
| **SUMA** | **90.00 €** |

## Podsumowanie

PiChat łączy dostępność fizycznego asystenta głosowego z elastycznością interfejsu webowego, wszystko zasilane przez najnowocześniejsze modele AI. Postępując zgodnie z tą dokumentacją, możesz zbudować potężnego, konfigurowalnego asystenta, który działa zarówno poprzez polecenia głosowe, jak i czat tekstowy.

Uproszczona architektura wykorzystująca natywne WebSockety zamiast dodatkowych usług komunikacyjnych idealna dla osobistego użytku jednego użytkownika. Dzięki temu rozwiązanie jest ekonomiczne, łatwiejsze w implementacji i utrzymaniu, zachowując jednocześnie wszystkie kluczowe funkcje synchronizacji w czasie rzeczywistym.

Modularna architektura pozwala na łatwą personalizację i rozszerzenie, czyniąc go odpowiednim dla szerokiego zakresu zastosowań, od osobistych asystentów po narzędzia edukacyjne i wiele innych.
