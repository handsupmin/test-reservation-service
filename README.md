# 시험 일정 예약 시스템 API

## 개요

이 API는 고객과 어드민이 각각의 필요에 맞게 시험 일정 예약을 처리할 수 있도록 합니다. 고객 및 어드민은 예약 가능한 시간을 확인하고, 예약을 생성, 수정, 확정, 삭제할 수 있습니다.

## 인증

모든 엔드포인트는 유효한 토큰이 필요합니다. 각 요청의 `Authorization` 헤더에 `Bearer Token` 형식으로 토큰을 전달해야 합니다.  
단, 편의를 위해 추가한 `GET /refresh_token` 엔드포인트는 토큰 없이도 사용 가능합니다.

편의상 간소하게 구현하여 DB 초기화 시 아래 토큰이 생성됩니다.

| idx | user\_idx | user\_type | token  | expired\_at | created\_at | updated\_at |
|:----|:----------|:-----------|:-------|:------------|:------------|:------------|
| 1   | 1         | admin      | admin1 | ...         | ...         | ...         |
| 2   | 2         | admin      | admin2 | ...         | ...         | ...         |
| 3   | 3         | admin      | admin3 | ...         | ...         | ...         |
| 4   | 1         | user       | user1  | ...         | ...         | ...         |
| 5   | 2         | user       | user2  | ...         | ...         | ...         |
| 6   | 3         | user       | user3  | ...         | ...         | ...         |
| 7   | 4         | user       | user4  | ...         | ...         | ...         |
| 8   | 5         | user       | user5  | ...         | ...         | ...         |

모든 엔드포인트는 토큰 정보로 사용자를 판별합니다. `user_type`이 `admin`인 경우 어드민으로 간주합니다.

## 로컬 환경에서 실행하기

### 1. 환경 설정

로컬 환경에서 애플리케이션을 실행하려면, 먼저 환경 설정을 해야 합니다.

1. **`.env` 파일 생성:**
    - 프로젝트 루트 디렉토리에 있는 `.env-sample` 파일을 복사하여 `.env` 파일을 만듭니다.
    - 필요에 따라 다음과 같은 변수들의 값을 수정할 수 있습니다:
        - `POSTGRES_USER`: PostgreSQL 데이터베이스의 사용자 이름
        - `POSTGRES_PASSWORD`: PostgreSQL 데이터베이스의 비밀번호
        - `POSTGRES_DB`: PostgreSQL 데이터베이스의 이름
        - `EXTERNAL_APP_PORT`: 도커 외부에서 접근 가능한 애플리케이션에 포트 번호
        - `EXTERNAL_DB_PORT`: 도커 외부에서 접근 가능한 데이터베이스 포트 번호

   예시:
   ```
    POSTGRES_USER=username
    POSTGRES_PASSWORD=password
    POSTGRES_DB=postgres
    POSTGRES_HOST=db
    POSTGRES_PORT=5432
    
    EXTERNAL_APP_PORT=8080
    EXTERNAL_DB_PORT=5433
   ```

### 2. 도커 컨테이너 실행

1. **도커 컴포즈 실행:**
    - `docker-compose.yaml` 파일이 있는 경로에서 터미널을 열고 아래 명령어를 실행합니다.

   ```bash
   docker-compose up --build -d
   ```

   이 명령어는 도커 컨테이너를 빌드하고, 백그라운드에서 컨테이너를 실행합니다. 컨테이너가 실행되면, 로컬 환경에서 애플리케이션을 사용할 수 있습니다.

--- 

## APIs

### 1. 예약 가능한 시간 & 인원 조회

**엔드포인트:** `GET /api/reservations/available`

지정된 날짜에 예약 가능한 시간을 조회합니다.

**파라미터:**

- `date` (str): 예약 가능 여부를 확인할 날짜. `YYYY-MM-DD` 형식이어야 합니다.

**응답:**

- `200 OK`: 예약 가능한 시간과 남은 인원을 반환합니다.
- `400 Bad Request`: 날짜 형식이 잘못되었습니다.

**예시 요청:**

```http
GET /api/reservations/available?date=2024-09-10
Authorization: Bearer user1
```

**예시 응답:**
요청한 날짜에 예약 가능한 시간대를 반환합니다. 아래에 해당하는 경우 시간대가 표시되지 않습니다.

1) 해당 시간대에 예약이 꽉 찬 경우 (=이미 5만건의 예약이 확정된 경우)
2) (고객 전용) 해당 시간대에 본인의 확정된 예약건이 존재하는 경우

```json
[
  {
    "time": "00:00 ~ 01:00",
    "available_count": 50000
  },
  {
    "time": "01:00 ~ 02:00",
    "available_count": 40000
  },
  // 02:00 ~ 03:00은 예약이 꽉 찼습니다.
  {
    "time": "03:00 ~ 04:00",
    "available_count": 40000
  },
  ...
]
```

### 2. 예약 조회

**엔드포인트:** `GET /api/reservations`

등록된 예약 목록을 조회합니다.

**파라미터:**

- `date` (optional, str): 특정 날짜로 필터링 (`YYYY-MM-DD` 형식), `null`이면 전체 날짜 조회.
- `size` (optional, int): 한 페이지에 표시할 레코드 수.
- `page` (optional, int): 조회할 페이지 번호.

\*`size`와 `page` 파라미터는 함께 사용되어야 합니다.

**응답:**

- `200 OK`: 예약 목록을 반환합니다.
- `400 Bad Request`: 날짜 형식이 잘못되었거나, size/page 파라미터가 함께 사용되지 않았습니다.

**예시 요청:**

```http
GET /api/reservations?date=2024-09-10&size=10&page=1
Authorization: Bearer user1
```

**예시 응답:**

```json
[
  {
    "idx": 1,
    "user_idx": 1,
    "start_time": "2024-09-10 01:00:00",
    "end_time": "2024-09-10 04:00:00",
    "applicant_count": 10000,
    "state": "confirmed"
  },
  {
    "idx": 2,
    "user_idx": 1,
    "start_time": "2024-09-10 04:00:00",
    "end_time": "2024-09-10 05:00:00",
    "applicant_count": 20000,
    "state": "pending"
  }
]
```

### 3. 예약 신청

**엔드포인트:** `POST /api/reservations`

시험 일정 예약을 신청합니다.  
예약은 시험 시작 3일 전까지 신청 가능합니다.  
일정이 겹치는 예약이 존재하는지, 신청 가능한 인원 초과 여부를 확인합니다.

**요청:**

- `start_time` (datetime): 예약 시작 시간.
- `end_time` (datetime): 예약 종료 시간.
- `applicant_count` (int): 신청자 수.

\*`start_time`과 `end_time`은 둘 다 입력되어야 하며, `start_time`은 `end_time`보다 빨라야 합니다.  
\*`applicant_count`는 1 이상 50000 이하이어야 합니다.

**응답:**

- `200 OK`: 생성된 예약 정보를 반환합니다.
- `400 Bad Request`: 잘못된 입력, 시험 기간 임박 또는 예약 중복이 발생했습니다.
- `403 Forbidden`: 어드민은 예약 할 수 없습니다.

**예시 요청:**

```http
POST /api/reservations
Authorization: Bearer user2
Content-Type: application/json

{
    "start_time": "2024-09-10 09:00:00",
    "end_time": "2024-09-10 10:00:00",
    "applicant_count": 20000
}
```

**예시 응답:**

```json
{
  "idx": 1,
  "user_idx": 2,
  "start_time": "2024-09-10 09:00:00",
  "end_time": "2024-09-10 10:00:00",
  "applicant_count": 20000,
  "state": "pending"
}
```

### 4. 예약 확정

**엔드포인트:** `PUT /api/reservations/confirm`

**어드민 전용**  
예약 ID 목록을 받아 여러 예약을 확정합니다.  
고객의 예약 신청 후, 어드민이 이를 확인하고 확정을 통해 예약이 최종적으로 시험 운영 일정에 반영됩니다.  
확정되지 않은 예약은 최대 인원 수 계산에 포함되지 않습니다.  
일정이 겹치는 예약이 존재하는지, 신청 가능한 인원 초과 여부를 확인합니다.  
확정에 실패한 경우 이유를 알려줍니다.

**요청:**

- `reservation_idx_list` (list of int): 확정할 예약 ID 목록.

**응답:**

- `200 OK`: 확정되지 않은 예약 ID와 오류 세부 정보를 반환합니다.
- `400 Bad Request`: 유효성 검사 오류 또는 사용자가 어드민이 아닙니다.

**예시 요청:**

```http
PUT /api/reservations/confirm
Authorization: Bearer admin1
Content-Type: application/json

{
    "reservation_idx_list": [1, 2, 3, 4, 5, 6, 7]
}
```

**예시 응답:**

```json
{
  "result": [
    {
      "idx": 2,
      "detail": "삭제된 예약 정보입니다."
    },
    {
      "idx": 5,
      "detail": "일정이 겹치는 예약 정보가 존재합니다."
    },
    {
      "idx": 6,
      "detail": "일정이 겹치는 예약 정보가 존재합니다."
    }
  ]
}
```

### 5. 예약 수정

**엔드포인트:** `PUT /api/reservations`

신청한 예약 정보를 수정합니다.  
고객은 예약 확정 전에 본인 예약을 수정할 수 있습니다.  
어드민은 모든 고객의 예약을 확정할 수 있습니다.  
어드민은 고객 예약을 수정할 수 있습니다.

수정될 정보와 일정이 겹치는 예약이 존재하는지, 신청 가능한 인원 초과 여부를 확인합니다.

**요청:**

- `idx` (int): 수정할 예약의 ID.
- `start_time` (optional, datetime): 신규 시작 시간.
- `end_time` (optional, datetime): 신규 종료 시간.
- `applicant_count` (optional, int): 신규 신청자 수.
- `state` (optional, string): 예약 상태.

**응답:**

- `200 OK`: 수정된 예약 정보를 반환합니다.
- `400 Bad Request`: 유효성 검사 오류.

**예시 요청:**

```http
PUT /api/reservations
Authorization: Bearer user1
Content-Type: application/json

{
    "idx": 4,
    "start_time": "2024-09-10 10:00:00",
    "end_time": "2024-09-10 11:00:00",
    "applicant_count": 10000,
    "state": "pending"
}
```

**예시 응답:**

```json
{
  "idx": 4,
  "user_idx": 1,
  "start_time": "2024-09-10 10:00:00",
  "end_time": "2024-09-10 11:00:00",
  "applicant_count": 7,
  "state": "pending"
}
```

### 6. 예약 삭제

**엔드포인트:** `DELETE /api/reservations`

기존 예약을 취소 상태로 변경합니다.  
고객은 확정 전에 본인 예약을 삭제할 수 있습니다.  
어드민은 모든 고객의 예약을 삭제할 수 있습니다.

**요청:**

- `idx` (int): 삭제할 예약의 ID.

**응답:**

- `200 OK`: 성공 메시지를 반환합니다.
- `400 Bad Request`: 유효성 검사 오류.

**예시 요청:**

```http
DELETE /api/reservations
Authorization: Bearer user1
Content-Type: application/json

{
    "idx": 1
}
```

**예시 응답:**

```json
{
  "state": "success"
}
```

---
