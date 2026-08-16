"""API endpoint paths and protocol-level constants."""
from __future__ import annotations


class Endpoint:
    """Main-backend (BASE_API_URL) paths."""
    PROFILE = "api/v8/profile"
    BALANCE = "api/v8/packages/balance-and-credit"
    QUOTA_DETAILS = "api/v8/packages/quota-details"
    FAMILY_LIST = "api/v8/xl-stores/options/list"
    PACKAGE_DETAIL = "api/v8/xl-stores/options/detail"
    ADDONS = "api/v8/xl-stores/options/addons-pinky-box"
    INTERCEPT_PAGE = "misc/api/v8/utility/intercept-page"
    NOTIFICATIONS = "api/v8/notification-non-grouping"
    NOTIFICATION_DETAIL = "api/v8/notification/detail"
    TRANSACTION_HISTORY = "payments/api/v8/transaction-history"
    TIERING_INFO = "gamification/api/v8/loyalties/tiering/info"
    UNSUBSCRIBE = "api/v8/packages/unsubscribe"

    # Store
    STORE_SEGMENTS = "api/v8/configs/store/segments"
    FAMILY_LIST_SEARCH = "api/v8/xl-stores/options/search/family-list"
    STORE_PACKAGES_SEARCH = "api/v9/xl-stores/options/search"
    REDEEMABLES = "api/v8/personalization/redeemables"

    # Family Plan / Circle
    FAMILY_PLAN_MEMBER_INFO = "sharings/api/v8/family-plan/member-info"
    FAMILY_PLAN_CHANGE_MEMBER = "sharings/api/v8/family-plan/change-member"
    FAMILY_PLAN_REMOVE_MEMBER = "sharings/api/v8/family-plan/remove-member"
    FAMILY_PLAN_ALLOCATE_QUOTA = "sharings/api/v8/family-plan/allocate-quota"
    FAMILY_PLAN_VALIDATE_MSISDN = "api/v8/auth/check-dukcapil"

    CIRCLE_GROUP_STATUS = "family-hub/api/v8/groups/status"
    CIRCLE_GROUP_CREATE = "family-hub/api/v8/groups/create"
    CIRCLE_ACCEPT_INVITATION = "family-hub/api/v8/groups/accept-invitation"
    CIRCLE_MEMBERS_INFO = "family-hub/api/v8/members/info"
    CIRCLE_MEMBERS_VALIDATE = "family-hub/api/v8/members/validate"
    CIRCLE_MEMBERS_INVITE = "family-hub/api/v8/members/invite"
    CIRCLE_MEMBERS_REMOVE = "family-hub/api/v8/members/remove"
    CIRCLE_SPENDING_TRACKER = "gamification/api/v8/family-hub/spending-tracker"
    CIRCLE_BONUS_LIST = "gamification/api/v8/family-hub/bonus/list"

    # Registration
    DUKCAPIL = "api/v8/auth/regist/dukcapil"

    # Payment
    PAYMENT_METHODS_OPTION = "payments/api/v8/payment-methods-option"
    SETTLEMENT_MULTIPAYMENT = "payments/api/v8/settlement-multipayment"
    SETTLEMENT_QRIS = "payments/api/v8/settlement-multipayment/qris"
    SETTLEMENT_EWALLET = "payments/api/v8/settlement-multipayment/ewallet"
    PENDING_DETAIL = "payments/api/v8/pending-detail"

    # Gamification / Loyalty
    BOUNTIES_EXCHANGE = "api/v8/personalization/bounties-exchange"
    LOYALTIES_EXCHANGE = "gamification/api/v8/loyalties/tiering/exchange"
    BOUNTIES_ALLOTMENT = "gamification/api/v8/loyalties/tiering/bounties-allotment"


class CIAMEndpoint:
    """CIAM (BASE_CIAM_URL) paths."""
    OTP = "/realms/xl-ciam/auth/otp"
    EXTEND_SESSION = "/realms/xl-ciam/auth/extend-session"
    TOKEN = "/realms/xl-ciam/protocol/openid-connect/token"


class MigrationType:
    NONE = "NONE"
    PRE_TO_PRIOH = "PRE_TO_PRIOH"
    PRIOH_TO_PRIO = "PRIOH_TO_PRIO"
    PRIO_TO_PRIOH = "PRIO_TO_PRIOH"
    ALL = (NONE, PRE_TO_PRIOH, PRIOH_TO_PRIO, PRIO_TO_PRIOH)


class PaymentMethod:
    BALANCE = "BALANCE"
    QRIS = "QRIS"


class PaymentFor:
    BUY_PACKAGE = "BUY_PACKAGE"
    SHARE_PACKAGE = "SHARE_PACKAGE"
    REDEEM_VOUCHER = "REDEEM_VOUCHER"


class HttpHeader:
    HOST = "host"
    CONTENT_TYPE = "content-type"
    USER_AGENT = "user-agent"
    X_API_KEY = "x-api-key"
    AUTHORIZATION = "authorization"
    X_HV = "x-hv"
    X_SIGNATURE_TIME = "x-signature-time"
    X_SIGNATURE = "x-signature"
    X_REQUEST_ID = "x-request-id"
    X_REQUEST_AT = "x-request-at"
    X_VERSION_APP = "x-version-app"


class CIAMHeader:
    AX_DEVICE_ID = "Ax-Device-Id"
    AX_FINGERPRINT = "Ax-Fingerprint"
    AX_REQUEST_AT = "Ax-Request-At"
    AX_REQUEST_DEVICE = "Ax-Request-Device"
    AX_REQUEST_DEVICE_MODEL = "Ax-Request-Device-Model"
    AX_REQUEST_ID = "Ax-Request-Id"
    AX_SUBSTYPE = "Ax-Substype"
    AX_API_SIGNATURE = "Ax-Api-Signature"
    ACCEPT_ENCODING = "Accept-Encoding"


LANG_EN = "en"
