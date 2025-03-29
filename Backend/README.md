# Backend PiChat

## Przegląd

Ten dokument opisuje architekturę backendu dla projektu PiChat AI Assistant. Backend jest napisany w języku Go (Golang) i zapewnia funkcjonalność WebSocket do obsługi całej komunikacji w czasie rzeczywistym między interfejsem webowym a interfejsem głosowym Raspberry Pi.

## Spis treści

1. [Stos technologiczny](#stos-technologiczny)
2. [Struktura projektu](#struktura-projektu)
3. [Protokół WebSocket](#protokół-websocket)
4. [Implementacja WebSocket](#implementacja-websocket)
5. [Schemat bazy danych](#schemat-bazy-danych)
6. [Uwierzytelnianie i autoryzacja](#uwierzytelnianie-i-autoryzacja)
7. [Zmienne środowiskowe](#zmienne-środowiskowe)
8. [Konfiguracja deweloperska](#konfiguracja-deweloperska)
9. [Konfiguracja Dockera](#konfiguracja-dockera)
10. [Wdrożenie na Azure](#wdrożenie-na-azure)
11. [Testowanie](#testowanie)

## Stos technologiczny

Backend wykorzystuje następujące technologie:

- **Go (Golang)** - Główny język programowania backendu
  - Dlaczego Go? Go doskonale sprawdza się w budowaniu współbieżnych usług sieciowych dzięki swoim lekkim gorutynom, ma doskonałe charakterystyki wydajnościowe i generuje pojedynczy plik binarny, co upraszcza konteneryzację.
  
- **Gorilla WebSocket** - Biblioteka do implementacji WebSocket
  - Zapewnia kompletną i szeroko stosowaną implementację protokołu WebSocket dla Go.
  
- **GORM** - Maper obiektowo-relacyjny do operacji na bazie danych
  - Upraszcza interakcje z bazą danych dzięki automatycznym migracjom i budowaniu zapytań.
  
- **Azure SQL** - Główna baza danych
  - Zapewnia zarządzane możliwości SQL z dobrą integracją z innymi usługami Azure.
  
- **Azure OpenAI** - Przetwarzanie AI
  - Integruje się z modelami GPT do rozumienia i generowania języka naturalnego.

- **Azure Speech Services** - Możliwości konwersji tekstu na mowę i mowy na tekst
  - Niezbędne dla funkcjonalności interfejsu głosowego.

- **Docker** - Konteneryzacja
  - Zapewnia spójne wdrażanie w różnych środowiskach.

## Struktura projektu

Projekt wykorzystuje wzorzec czystej architektury z wyraźnym podziałem odpowiedzialności:

```
backend/
├── cmd/
│   └── api/
│       └── main.go           # Punkt wejścia aplikacji
├── internal/
│   ├── config/               # Zarządzanie konfiguracją
│   ├── models/               # Modele danych i schemat bazy danych
│   ├── repositories/         # Warstwa dostępu do bazy danych
│   ├── services/             # Logika biznesowa
│   ├── websocket/
│   │   ├── client.go         # Obsługa pojedynczego klienta WebSocket
│   │   ├── hub.go            # Centrum zarządzania połączeniami
│   │   ├── handlers.go       # Obsługa wiadomości WebSocket
│   │   └── types.go          # Definicje typów wiadomości
│   └── middleware/           # Komponenty middleware
├── pkg/                      # Pakiety wielokrotnego użytku
│   ├── azure/                # Integracje z usługami Azure
│   ├── logger/               # Narzędzia do logowania
│   └── validator/            # Narzędzia do walidacji danych
├── scripts/                  # Skrypty automatyzacji
├── .dockerignore             # Pliki do wykluczenia z kontekstu Dockera
├── .env.example              # Przykładowe zmienne środowiskowe
├── Dockerfile                # Instrukcje budowania Dockera
├── go.mod                    # Definicja modułu Go
├── go.sum                    # Sumy kontrolne modułu Go
└── README.md                 # Ten plik
```

### Objaśnienie struktury

#### `cmd/`
Zawiera główne punkty wejścia aplikacji. W projekcie Go, katalog `cmd` zazwyczaj zawiera główne pakiety wykonywalne.

#### `internal/`
Zawiera pakiety specyficzne dla tej aplikacji, które nie są przeznaczone do importowania przez inne projekty.

- **`config/`** - Zarządza konfiguracją aplikacji ładowaną ze zmiennych środowiskowych i plików konfiguracyjnych.
- **`models/`** - Definiuje struktury danych reprezentujące tabele bazy danych i encje domenowe.
- **`repositories/`** - Implementuje warstwę dostępu do danych, obsługującą wszystkie operacje bazodanowe.
- **`services/`** - Zawiera logikę biznesową operującą na modelach.
- **`websocket/`** - Kompleksowa implementacja funkcjonalności WebSocket do komunikacji w czasie rzeczywistym, włączając obsługę klientów, zarządzanie połączeniami i przetwarzanie wiadomości.
- **`middleware/`** - Middleware dla przekrojowych zagadnień jak uwierzytelnianie, logowanie i obsługa błędów.

#### `pkg/`
Zawiera pakiety wielokrotnego użytku, które potencjalnie mogłyby być używane przez inne projekty.

- **`azure/`** - Integracja z usługami Azure (OpenAI, Speech, itp.).
- **`logger/`** - Scentralizowana konfiguracja logowania.
- **`validator/`** - Narzędzia do walidacji danych.

## Protokół WebSocket

W aplikacji PiChat, cała komunikacja między klientami (interfejs webowy i Raspberry Pi) a serwerem odbywa się poprzez protokół WebSocket. Protokół ten pozwala na dwukierunkową komunikację w czasie rzeczywistym, co jest idealne dla czatu i synchronizacji.

### Struktura wiadomości

Wiadomości WebSocket są strukturyzowane jako JSON w następującym formacie:

```json
{
  "action": "string",
  "payload": {}
}
```

Pole `action` określa typ operacji, a `payload` zawiera dane związane z tą operacją.

### Główne operacje WebSocket

#### Zarządzanie konwersacjami

- **`get_conversations`** - Pobieranie listy konwersacji
  ```json
  { "action": "get_conversations" }
  ```
  Odpowiedź:
  ```json
  {
    "action": "conversations_list",
    "payload": {
      "conversations": [
        { "id": "uuid", "title": "Tytuł", "last_message_at": "timestamp" }
      ]
    }
  }
  ```

- **`create_conversation`** - Tworzenie nowej konwersacji
  ```json
  { "action": "create_conversation", "payload": { "title": "Nowa rozmowa" } }
  ```

- **`get_conversation`** - Pobieranie szczegółów konwersacji
  ```json
  { "action": "get_conversation", "payload": { "id": "uuid" } }
  ```

- **`update_conversation`** - Aktualizacja tytułu konwersacji
  ```json
  { "action": "update_conversation", "payload": { "id": "uuid", "title": "Nowy tytuł" } }
  ```

- **`delete_conversation`** - Usuwanie konwersacji
  ```json
  { "action": "delete_conversation", "payload": { "id": "uuid" } }
  ```

#### Zarządzanie wiadomościami

- **`send_message`** - Wysyłanie nowej wiadomości
  ```json
  {
    "action": "send_message",
    "payload": {
      "conversation_id": "uuid",
      "content": "Treść wiadomości",
      "is_audio": false
    }
  }
  ```

- **`get_messages`** - Pobieranie historii wiadomości
  ```json
  { "action": "get_messages", "payload": { "conversation_id": "uuid" } }
  ```

#### Ustawienia użytkownika

- **`get_settings`** - Pobieranie ustawień użytkownika
  ```json
  { "action": "get_settings" }
  ```

- **`update_settings`** - Aktualizacja ustawień użytkownika
  ```json
  {
    "action": "update_settings",
    "payload": {
      "selected_model": "gpt-4",
      "voice_settings": { "gender": "female", "accent": "polish" }
    }
  }
  ```

#### Usługi mowy

- **`text_to_speech`** - Konwersja tekstu na mowę
  ```json
  {
    "action": "text_to_speech",
    "payload": {
      "text": "Tekst do konwersji",
      "voice_settings": { "gender": "female", "accent": "polish" }
    }
  }
  ```

- **`speech_to_text`** - Konwersja mowy na tekst (dane audio przesyłane jako base64)
  ```json
  {
    "action": "speech_to_text",
    "payload": {
      "audio_data": "base64_encoded_audio"
    }
  }
  ```

### Strumieniowanie odpowiedzi AI

Dla odpowiedzi AI, backend wykorzystuje strumieniowanie tokenów poprzez WebSockety:

```json
{
  "action": "message_stream",
  "payload": {
    "conversation_id": "uuid",
    "message_id": "uuid",
    "token": "fragment tekstu",
    "finished": false
  }
}
```

Klient otrzymuje serię takich wiadomości i składa je w pełną odpowiedź. Ostatnia wiadomość ma `finished: true`.

### Powiadomienia i zdarzenia

System wysyła również powiadomienia do połączonych klientów:

- **`typing_indicator`** - Wskazuje, że AI generuje odpowiedź
- **`conversation_updated`** - Powiadomienie o zaktualizowaniu konwersacji
- **`conversation_deleted`** - Powiadomienie o usunięciu konwersacji
- **`new_message`** - Powiadomienie o nowej wiadomości

## Implementacja WebSocket

### Zarządzanie połączeniami

Centrum zarządzania połączeniami (Hub) odpowiada za:

- Rejestrację nowych klientów WebSocket
- Usuwanie rozłączonych klientów
- Rozsyłanie wiadomości do klientów

```go
// Uproszczony przykład implementacji Hub
type Hub struct {
    clients    map[*Client]bool
    register   chan *Client
    unregister chan *Client
    broadcast  chan []byte
    mutex      sync.Mutex
}
```

### Obsługa klienta

Każdy klient WebSocket jest obsługiwany przez dedykowaną gorutynę:

```go
// Uproszczony przykład implementacji Client
type Client struct {
    hub      *Hub
    conn     *websocket.Conn
    send     chan []byte
    userID   string
}
```

### Przepływ danych

1. Klient łączy się z endpointem WebSocket
2. Uwierzytelnianie odbywa się poprzez token w nagłówku lub parametrze zapytania
3. Po pomyślnym uwierzytelnieniu, klient jest rejestrowany w hubie
4. Klient może wysyłać wiadomości JSON zgodnie z protokołem
5. Hub przetwarza wiadomości i rozsyła odpowiedzi do odpowiednich klientów

### Mechanizm obsługi wiadomości

Backend używa mechanizmu podobnego do routera, który kieruje przychodzące wiadomości do odpowiednich handlerów na podstawie pola `action`:

```go
// Uproszczony przykład
func (h *Hub) handleMessage(client *Client, message []byte) {
    var request WebSocketRequest
    if err := json.Unmarshal(message, &request); err != nil {
        // obsługa błędu
        return
    }
    
    switch request.Action {
    case "get_conversations":
        h.handleGetConversations(client, request.Payload)
    case "send_message":
        h.handleSendMessage(client, request.Payload)
    // pozostałe akcje...
    default:
        // nieznana akcja
    }
}
```

## Schemat bazy danych

Schemat bazy danych zawiera następujące główne encje:

### Użytkownik (User)

Przechowuje informacje o użytkowniku i ustawienia. Dla systemu jednoosobowego będzie zawierać tylko jeden rekord.

### Konwersacja (Conversation)

Przechowuje metadane o konwersacjach:
- ID (UUID)
- Tytuł (Title)
- DataUtworzenia (CreatedAt)
- DataAktualizacji (UpdatedAt)
- DataOstatniejWiadomości (LastMessageAt)

### Wiadomość (Message)

Przechowuje poszczególne wiadomości:
- ID (UUID)
- IDKonwersacji (ConversationID, klucz obcy)
- Rola (Role, użytkownik/asystent)
- Treść (Content)
- DataUtworzenia (CreatedAt)
- PlikAudio (AudioFile, opcjonalnie, dla wiadomości głosowych)

### UstawieniaUżytkownika (UserSettings)

Przechowuje preferencje użytkownika:
- WybranyModel (SelectedModel, GPT-4/GPT-3.5)
- UstawieniaGłosu (VoiceSettings, płeć, akcent, prędkość)
- OsobowośćAsystenta (AssistantPersonality)

## Uwierzytelnianie i autoryzacja

Dla uproszczenia, system używa prostego uwierzytelniania opartego na tokenie API. W systemie jednoosobowym zapewnia to odpowiednie bezpieczeństwo przy minimalizacji złożoności.

Przepływ uwierzytelniania:
1. Token API jest generowany podczas początkowej konfiguracji
2. Token jest przechowywany w zmiennych środowiskowych
3. Klienci WebSocket dołączają token jako parametr zapytania: `wss://server/ws?token=API_TOKEN`
4. Serwer weryfikuje token przed ustanowieniem połączenia WebSocket

## Zmienne środowiskowe

Aplikacja wymaga następujących zmiennych środowiskowych:

```
# Konfiguracja serwera
SERVER_PORT=8080
API_TOKEN=twój_bezpieczny_token_tutaj
ENVIRONMENT=development

# Usługi Azure
AZURE_OPENAI_ENDPOINT=https://twój-serwis-openai.openai.azure.com/
AZURE_OPENAI_KEY=twój_klucz_openai
AZURE_OPENAI_DEPLOYMENT_GPT4=nazwa_wdrożenia
AZURE_OPENAI_DEPLOYMENT_GPT35=nazwa_wdrożenia

AZURE_SPEECH_KEY=twój_klucz_speech
AZURE_SPEECH_REGION=eastus

# Baza danych
DB_HOST=twój_host_db.database.windows.net
DB_NAME=pichat
DB_USER=pichat_admin
DB_PASSWORD=twoje_bezpieczne_hasło
DB_PORT=1433
```

## Konfiguracja deweloperska

### Wymagania wstępne

- Go 1.18 lub nowszy
- Docker i Docker Compose (dla rozwoju w kontenerach)
- Konto Azure z wymaganymi usługami

### Lokalny rozwój

1. Sklonuj repozytorium
   ```
   git clone https://github.com/karolk75/PiChat.git
   cd pichat/backend
   ```

2. Skopiuj przykładowy plik środowiskowy i zaktualizuj go swoimi ustawieniami
   ```
   cp .env.example .env
   ```

3. Zainstaluj zależności
   ```
   go mod download
   ```

4. Uruchom aplikację
   ```
   go run cmd/api/main.go
   ```

5. Serwer WebSocket będzie dostępny pod adresem `ws://localhost:8080/ws`

## Konfiguracja Dockera

Aplikacja zawiera plik Dockerfile do konteneryzacji:

```Dockerfile
FROM golang:1.18-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o api ./cmd/api

FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /root/

COPY --from=builder /app/api .
COPY --from=builder /app/.env .

EXPOSE 8080

CMD ["./api"]
```

### Budowanie i uruchamianie kontenera Dockera

```bash
# Zbuduj obraz Dockera
docker build -t pichat-backend .

# Uruchom kontener
docker run -p 8080:8080 --env-file .env pichat-backend
```

## Wdrożenie na Azure

### Konfiguracja Azure App Service

1. Utwórz Azure App Service z obsługą Dockera
   ```bash
   az appservice plan create --name pichat-service-plan --resource-group pichat-rg --sku B1 --is-linux
   az webapp create --resource-group pichat-rg --plan pichat-service-plan --name pichat-backend --deployment-container-image-name pichat-backend
   ```

2. Skonfiguruj zmienne środowiskowe w App Service
   ```bash
   az webapp config appsettings set --resource-group pichat-rg --name pichat-backend --settings @env-settings.json
   ```

3. Włącz WebSockety w App Service (kluczowe dla komunikacji WebSocket)
   ```bash
   az webapp config set --resource-group pichat-rg --name pichat-backend --web-sockets-enabled true
   ```

### Ciągłe wdrażanie

Repozytorium może być skonfigurowane z GitHub Actions lub Azure DevOps do ciągłego wdrażania:

1. Zbuduj obraz Dockera
2. Wypchnij do Azure Container Registry
3. Wdróż do Azure App Service

## Testowanie

Backend zawiera kompleksowe testy dla wszystkich komponentów:

### Uruchamianie testów

```bash
# Uruchom wszystkie testy
go test ./...

# Uruchom testy z pokryciem
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

### Struktura testów

- **Testy jednostkowe**: Testują poszczególne funkcje i metody
- **Testy integracyjne**: Testują interakcje między komponentami
- **Testy WebSocket**: Testują obsługę protokołu WebSocket i przetwarzanie wiadomości

## Optymalizacja wydajności

- **Pula połączeń**: Połączenia z bazą danych są grupowane w pule dla zwiększenia wydajności
- **Gorutyny**: Lekkie wątki do obsługi jednoczesnych połączeń WebSocket
- **Ograniczanie przepustowości**: Zapobiega nadużyciom i zapewnia sprawiedliwy podział zasobów
- **Buforowanie**: Często używane dane są buforowane w celu zmniejszenia obciążenia bazy danych
- **Odpowiedzi strumieniowe**: Odpowiedzi AI są strumieniowane, aby zmniejszyć postrzeganą latencję 