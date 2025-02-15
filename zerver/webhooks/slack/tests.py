from typing_extensions import override

from zerver.lib.test_classes import WebhookTestCase


class SlackWebhookTests(WebhookTestCase):
    STREAM_NAME = "slack"
    URL_TEMPLATE = "/api/v1/external/slack?stream={stream}&api_key={api_key}"
    WEBHOOK_DIR_NAME = "slack"

    def test_slack_channel_to_topic(self) -> None:
        expected_topic_name = "channel: general"
        expected_message = "**slack_user**: test"
        self.check_webhook(
            "message_info",
            expected_topic_name,
            expected_message,
            content_type="application/x-www-form-urlencoded",
        )

    def test_slack_channel_to_stream(self) -> None:
        self.STREAM_NAME = "general"
        self.url = "{}{}".format(self.url, "&channels_map_to_topics=0")
        expected_topic_name = "Message from Slack"
        expected_message = "**slack_user**: test"
        self.check_webhook(
            "message_info",
            expected_topic_name,
            expected_message,
            content_type="application/x-www-form-urlencoded",
        )

    def test_missing_data_user_name(self) -> None:
        payload = self.get_body("message_info_missing_user_name")
        url = self.build_webhook_url()
        result = self.client_post(url, payload, content_type="application/x-www-form-urlencoded")
        self.assert_json_error(result, "Missing 'user_name' argument")

    def test_missing_data_channel_name(self) -> None:
        payload = self.get_body("message_info_missing_channel_name")
        url = self.build_webhook_url()
        result = self.client_post(url, payload, content_type="application/x-www-form-urlencoded")
        self.assert_json_error(result, "Missing 'channel_name' argument")

    def test_missing_data_text(self) -> None:
        payload = self.get_body("message_info_missing_text")
        url = self.build_webhook_url()
        result = self.client_post(url, payload, content_type="application/x-www-form-urlencoded")
        self.assert_json_error(result, "Missing 'text' argument")

    def test_invalid_channels_map_to_topics(self) -> None:
        payload = self.get_body("message_info")
        url = "{}{}".format(self.url, "&channels_map_to_topics=abc")
        result = self.client_post(url, payload, content_type="application/x-www-form-urlencoded")
        self.assert_json_error(result, "Error: channels_map_to_topics parameter other than 0 or 1")

    @override
    def get_body(self, fixture_name: str) -> str:
        return self.webhook_fixture_data("slack", fixture_name, file_type="txt")
