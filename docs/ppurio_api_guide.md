1
뿌리오 연동 규격

1
HTTPS
- 안전한 데이터 전송을 위해 모든 API 요청은 SSL 환경의 HTTPS(443)를 사용해야 합니다.

2
UTF-8
- UTF-8 인코딩은 다양한 언어와 스크립트의 광범위한 문자를 지원하기 위해 기본적으로 제공됩니다.

3
가이드 작성 환경 정보
- java: JDK17
- python: Python 3.10.8
- php: php5

*테스트 시 보안 등급 / 서버 스펙 확인 (OS 및 프로그램, TLS 버전 등)
*개발 환경에서 발생한 오류는 각 본인 환경에 맞는 설정이 있기에 도움을 드리기 어렵습니다.
*버전이 업그레이드될수록 지원하지 않는 메서드가 있을 수 있어 요청 실패가 나올 수 있습니다.
*연동 발송은 변수8 까지 지원합니다.

2
요청값 정의

경로	설명
/v1/token	POST	Access Token 발급을 요청하는 기능입니다.
/v1/kakao	카카오톡(알림톡) 전송을 요청하는 기능입니다.
/v1/cancel/kakao	카카오톡(알림톡) 예약발송을 취소하는 기능입니다.
*인증키 : 뿌리오 아이디를 대신하는 고유 값
*인증 토큰 : 유효 시간이 24시간 제한적으로 사용할 수 있는 인증 정보값
3
엑세스 토큰 발급

- 메시지, 카카오톡 발송 API 서비스를 이용하기 위해서 엑세스 토큰을 발급하기 위한 API입니다.
- 엑세스 토큰의 유효 시간은 24시간이며, 이후에는 사용이 불가하고 재발급이 필요합니다.
- Rate-Limit이 변경되거나 연동 IP를 추가하는 경우, 그리고 인증키를 재발급 받은 경우 엑세스 토큰 재발급이 필요합니다.
- Authorization 헤더에 뿌리오 계정과 연동 페이지에서 발급 받은 인증키를 Base64 인코딩한 문자열을 입력합니다.
- 연동IP 등록 및 인증키 발급이 선행되어야 합니다. 연동 > 연동 관리에서 확인 가능합니다.

Request

1. 요청 헤더

요청 헤더	설명
Authorization	"뿌리오 계정 : 연동 개발 인증키”를 Base64 인코딩한 문자열을 전달하는 헤더
Authorization : Basic {Base64 인코딩한 문자열}
Response

1. 응답 바디

필드	타입	필수	설명
token	text	Y	인증 토큰
type	text(6)	Y	Bearer
expired	text(14)	Y	토큰 만료 시간
2. 예시

HTTP/1.1 200 OK
Content-Type: application/json;charset=UTF-8
{
 "token":  “eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInVzZXJuYW1lIjoiam9obmRvZSIsImV4cCI6MTY5MjM4ODgwMH0.BJYd2Urr4nU6J1R6RBOlhJpSdSv3zmyl3vr_-F7VjKk",
"type": "Bearer",
"expired": "20230414090407"
}
4
카카오톡(알림톡 텍스트, 이미지, 강조표기, 아이템리스트) 발송 요청

- 카카오톡 발송을 요청하는 API 입니다.
- API 사용을 위해서 엑세스 토큰 발급이 선행이 되어야 합니다.
- 자세한 발송 결과는 뿌리오 발송결과 페이지에서 확인할 수 있습니다.
- API 성공 응답을 받더라도 잔액부족, 발송한도 초과, 계정 사용불가와 같은 이유로 최종적으로 발송에 실패할수도 있습니다. 이러한 경우 문자연동 사용내역 > 발송 실패건 보기에서 확인할 수 있습니다.
- 추가 필드는 허용되지 않습니다.
- 치환 문구 사용 시 메시지 길이 초과로 인해 발송이 되지 않을 수 있습니다.
- MessageType 파라미터를 기준으로 재화가 차감됩니다.

Request

1. 요청 헤더

요청 헤더	설명
Authorization	엑세스 토큰을 전달하는 헤더, 토큰 타입은 “Bearer”로 고정
Authorization: Bearer {엑세스 토큰}
2. 요청 바디

필드	타입	필수	설명
account	text(20)	O	뿌리오 계정
messageType	text(3)	O	ALT/ALL/ALH/ALI
- ALT: 알림톡 기본형
- ALI: 알림톡 이미지
- ALH: 알림톡 강조표기
- ALL: 알림톡 아이템리스트
senderProfile	text(20)	O	발신 프로필명
- 뿌리오에서 발급받은 발신 프로필명(ex) @뿌리오)
templateCode	text(100)	O	템플릿 코드
- 뿌리오에서 발급받은 템플릿 코드
- 카카오톡 > 카카오톡 설정 > 알림톡 템플릿 관리에서 확인 가능
duplicateFlag	text(1)	O	수신 번호 중복 여부
- Y : 중복 허용
- N : 중복 제거
targetCount	number	O	수신자 목록 수
targets	array	O	수신자 목록
* 아래 targets 참조

refKey	text(32)	O	요청자가 부여한 키
isResend	text(1)	O	대체 발송 허용 여부
- Y : 대체 발송 허용
- N : 대체 발송 불가
sendTime	text(19)	X	예약 발송 시간
- yyyy-MM-DDTHH:mm:ss 형태
- 최소 3분 이후, 최대 다음 해 말일
- 요청에서 제외시 즉시 발송
resend	object	X	대체 발송 정보
* 아래 resend 참조

⦁ targets
- name은 content 필드의 [*이름*]에 치환됩니다.

필드	타입	필수	설명
to	text(16)	Y	수신 번호
changeWord	json	N	치환 문구 목록
* 아래 changeWord 참조

name	text(100)	N	[*이름*] 치환 문구
⦁ changeWord
- content 필드에 해당되는 변수([*1*] ~ [*8*])에 치환됩니다.
- 등록된 변수가 없는 번호는 빈칸으로 전송됩니다.

필드	타입	필수	설명	필드	타입	필수	설명
var1	text(100)	N	[*1*] 치환 문구	var5	text(100)	N	[*5*] 치환 문구
var2	text(100)	N	[*2*] 치환 문구	var6	text(100)	N	[*6*] 치환 문구
var3	text(100)	N	[*3*] 치환 문구	var7	text(100)	N	[*7*] 치환 문구
var4	text(100)	N	[*4*] 치환 문구	var8	text(100)	N	[*8*] 치환 문구
⦁ resend

필드	타입	필수	설명
messageType	text(3)	O	SMS/LMS/MMS
* MessageType 기준으로 재화가 차감됩니다.
content	text(2000)	O	메시지 내용
- SMS : 최대 90byte
- MMS, LMS : 최대 2000byte
from	text(16)	O	발신번호
subject	text(30)	X	제목
files	array	X	MMS 발송 시 첨부 파일
* 아래 files 참조

⦁ files
- MMS 발송 시 사용될 이미지이며, 최대 1개까지만 첨부가 가능합니다.
- 바이너리 형식인 이미지 파일을 Base64로 인코딩하여 텍스트로 입력하셔야 합니다.
- 파일 형식 및 크기 : jpg, jpeg, png, gif / 최대 400KB

필드	타입	필수	설명
name	text(200)	Y	파일 명
size	number	Y	파일 크기 (byte)
data	text	Y	업로드할 이미지 파일
Response

1. 응답 바디

필드	타입	필수	설명
code	text(4)	O	응답 코드
description	text	O	응답 메시지
refkey	text(32)	O	요청자가 부여한 키
messageKey	text(33)	O	메시지 고유 키
2. 응답 헤더

응답 헤더	설명
RateLimit-Limit	총 허용량
RateLimit-Remaining	남은 요청 허용량
RateLimit-Reset	다음 요청 제한 재설정까지 남은 시간
3. 예시

 HTTP/1.1 200 OK
 Content-Type: application/json;charset=UTF-8
 {
     "code": "1000",
     "description": "success",
     "refkey": "text",
     "messageKey": "230413110135117SMS029914servsUBn“
 }
4. 실패 이력
- 발송 API에서 성공 응답을 받더라도, 다음과 같은 이유로 발송 요청 자체에 실패한 경우 발송결과에서 확인할 수 없고 연동사용내역 > 발송 실패건 보기 에서 직접 확인하셔야 합니다.

실패 사유	설명
잔액 부족	잔액이 부족하여 발송에 실패한 경우입니다.
API 사용 불가	현재 계정이 API를 사용하지 못하는 상태입니다.
잘못된 유저 정보	현재 계정이 뿌리오 서비스를 사용하지 못하는 상태입니다.
차단된 발신번호	불법 발신번호로 등록된 번호입니다.
잘못된 발신번호	현재 발신번호가 사용하지 못하는 상태입니다.
발송 한도 초과	발송 일일 한도를 초과하였습니다.
서버 오류	서버에서 오류가 발생하였습니다.
예약 불가 시간	예약이 불가능한 시간입니다.
서버 점검 시간	뿌리오 서비스가 점검 중 입니다.
잘못된 MMS 이미지	올바르지 않은 MMS 이미지 입니다.
존재하지 않는 프로필	뿌리오 계정에 등록되지 않은 발신프로필입니다.
잘못된 프로필	현재 발신프로필이 사용 불가한 상태입니다.
템플릿 유형 불일치	messageType과 templateCode가 일치하지 않습니다.
존재하지 않는 템플릿	뿌리오 계정에 등록되지 않은 템플릿입니다.
잘못된 템플릿	현재 템플릿이 사용 불가한 상태입니다.
5
예약 취소

- 발송 예약을 취소하는 API 입니다.
- 현재 발송 중이거나, 발송예약 시간 1분 전에는 예약을 취소할 수 없습니다.
- API 사용을 위해서 엑세스 토큰 발급이 선행이 되어야 합니다.
- 추가 필드는 허용되지 않습니다.

Request

1. 요청 헤더

요청 헤더	설명
Authorization	엑세스 토큰을 전달하는 헤더, 토큰 타입은 “Bearer”로 고정
Authorization: Bearer {엑세스 토큰}
2. 요청 바디

필드	타입	필수	설명
account	text(20)	O	뿌리오 계정
messageKey	text(33)	O	메시지 고유 키
Response

1. 응답 바디

필드	타입	필수	설명
code	text(4)	O	응답 코드
description	text	O	응답 메시지
2. 응답 헤더

응답 헤더	설명
RateLimit-Limit	총 허용량
RateLimit-Remaining	남은 요청 허용량
RateLimit-Reset	다음 요청 제한 재설정까지 남은 시간
3. 예시

HTTP/1.1 200 OK
Content-Type: application/json;charset=UTF-8
{
    "code": "1000",
    "description": "success",
}
4. API 결과코드정의

상태 코드	결과 코드	결과 메시지	설명
200	1000	ok	성공
400	2000	(잘못된 파라미터에 따라 다름)	요청이 유효하지 않음
2001	잘못된 예약발송 취소 URL	URL이 유효하지 않음
3001	invalid basic Authentication	토큰 발급 호출 시, Authorization 헤더가 유효하지 않음
3002	jwt invalid token	토큰이 유효하지 않음
3003	invalid ip	아이피가 유효하지 않음
3004	invalid account	계정이 유효하지 않음
3005	invalid bearer	토큰이 유효하지 않음
3006	not empty authorization header	Authorization 헤더가 유효하지 않음
3007	jwt token issuance failed	엑세스 토큰 발행 실패
3008	too many request	너무 많은 요청 (Rate-Limit 관련)
4004	inactive account	api 접근 권한이 비활성화 상태
4006	invalid auth key	인증키가 유효하지 않음
4007	not issued auth key	인증키를 발행 받지 않음
4009	invalid message key	취소를 위한 messageKey가 유효하지 않음
4010	the deadline for canceling has expired	예약 취소 가능 시간이 지남
4011	the message has already been sent	메시지가 이미 발송중인 상태
4012	the reservation cannot be canceled	예약을 취소할 수 없음
500	9000 ~ 9999	internal server error	서버 오류
