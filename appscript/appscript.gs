// ============================================================
// Y-Union 카카오톡 알림톡 발송 Google Apps Script
// Google Form 제출 시 자동으로 환영 알림톡을 발송합니다.
// ============================================================

// 설정값
var CONFIG = {
  API_URL: "http://ppurio.y-union.org:7936/send_message",
  API_KEY: "ebeba5bb1e793cc703e5e09120d3e6d3dabd158d527130157ae1850efb030543",
  TEMPLATE_ID: "ppur_2026012921485212712316904",
  SLACK_WEBHOOK_URL:
    "https://hooks.slack.com/services/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",
};

/**
 * Google Form 제출 트리거 함수
 * Forms 에디터 > 트리거 > onFormSubmit 으로 등록
 */
function onFormSubmit(e) {
  var formResponse = e.response;
  var itemResponses = formResponse.getItemResponses();

  var name = "";
  var phoneNumber = "";

  for (var i = 0; i < itemResponses.length; i++) {
    var questionTitle = itemResponses[i].getItem().getTitle();
    var answer = itemResponses[i].getResponse();

    if (questionTitle === "이름") {
      name = answer;
    } else if (questionTitle === "휴대전화 번호") {
      phoneNumber = answer;
    }
  }

  // 전화번호 하이픈 및 공백 제거
  phoneNumber = phoneNumber.replace(/[-\s]/g, "");

  if (!name || !phoneNumber) {
    Logger.log(
      "이름 또는 전화번호가 비어있습니다. name=" + name + ", phone=" + phoneNumber
    );
    sendSlackNotification(false, name, phoneNumber, null, "이름 또는 전화번호 누락");
    return;
  }

  Logger.log("가입 신청 접수: 이름=" + name + ", 전화번호=" + phoneNumber);
  sendKakaoMessage(name, phoneNumber, CONFIG.TEMPLATE_ID);
}

/**
 * 카카오톡 알림톡 발송 요청
 */
function sendKakaoMessage(name, phoneNumber, templateId) {
  var options = {
    method: "post",
    contentType: "application/json",
    headers: { "x-api-key": CONFIG.API_KEY },
    payload: JSON.stringify({
      phoneNumber: phoneNumber,
      name: name,
      templateId: templateId,
    }),
    muteHttpExceptions: true,
  };

  try {
    var response = UrlFetchApp.fetch(CONFIG.API_URL, options);
    var responseCode = response.getResponseCode();
    var responseBody = response.getContentText();

    Logger.log("발송 응답: code=" + responseCode + ", body=" + responseBody);

    if (responseCode === 200) {
      var parsed = JSON.parse(responseBody);
      if (parsed.success) {
        Logger.log("카카오톡 발송 성공: " + name);
        sendSlackNotification(true, name, phoneNumber);
      } else {
        Logger.log("카카오톡 발송 실패 (API 응답): " + responseBody);
        sendSlackNotification(
          false,
          name,
          phoneNumber,
          responseCode,
          parsed.message
        );
      }
    } else {
      Logger.log("카카오톡 발송 실패: HTTP " + responseCode);
      sendSlackNotification(false, name, phoneNumber, responseCode, responseBody);
    }
  } catch (error) {
    Logger.log("카카오톡 발송 오류: " + error.toString());
    sendSlackNotification(false, name, phoneNumber, null, error.toString());
  }
}

/**
 * Slack 알림 발송
 */
function sendSlackNotification(
  isSuccess,
  name,
  phoneNumber,
  responseCode,
  error
) {
  if (!CONFIG.SLACK_WEBHOOK_URL) return;

  var statusEmoji = isSuccess ? "✅" : "❌";
  var statusText = isSuccess ? "성공" : "실패";

  var blocks = [
    {
      type: "section",
      text: {
        type: "mrkdwn",
        text: statusEmoji + " *카카오톡 메시지 발송 " + statusText + "*",
      },
    },
    {
      type: "section",
      fields: [
        { type: "mrkdwn", text: "*이름:*\n" + name },
        { type: "mrkdwn", text: "*휴대전화번호:*\n" + phoneNumber },
      ],
    },
  ];

  if (!isSuccess) {
    if (responseCode) {
      blocks.push({
        type: "section",
        text: { type: "mrkdwn", text: "*HTTP 상태 코드:*\n" + responseCode },
      });
    }
    if (error) {
      blocks.push({
        type: "section",
        text: { type: "mrkdwn", text: "*오류 메시지:*\n" + error },
      });
    }
  }

  blocks.push({
    type: "context",
    elements: [
      {
        type: "mrkdwn",
        text: "이 메시지는 Google Apps Script에서 자동으로 생성되었습니다.",
      },
    ],
  });

  try {
    UrlFetchApp.fetch(CONFIG.SLACK_WEBHOOK_URL, {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify({ blocks: blocks }),
    });
  } catch (e) {
    Logger.log("Slack 알림 발송 실패: " + e.toString());
  }
}

/**
 * 수동 테스트용 함수
 * Apps Script 에디터에서 직접 실행하여 테스트
 */
function sendManualKakaoMessage() {
  var name = "테스트";
  var phoneNumber = "01012345678";
  var templateId = CONFIG.TEMPLATE_ID;

  sendKakaoMessage(name, phoneNumber, templateId);
}
