from enum import Enum


class Fact(str, Enum):
    USER_PREFERENCE = "user_preference"
    PROJECT_DETAIL = "project_detail"
    TECH_STACK = "tech_stack"
    BUSINESS_RULE = "business_rule"
    MARKET_FIT = "market_fit"
    TEAM_INFO = "team_info"
    GENERAL = "general"


class Decision(str, Enum):
    ARCHITECTURE = "architecture"
    TECHNOLOGY = "technology"
    PRODUCT_FEATURE = "product_feature"
    TIMELINE = "timeline"
    RESOURCE_ALLOCATION = "resource_allocation"
    ORGANIZATIONAL = "organizational"
    GENERAL = "general"


class ConsideredOption(str, Enum):
    ALTERNATIVE = "alternative"
    COMPETING_TECH = "competing_tech"
    APPROACH = "approach"
    GENERAL = "general"


class Task(str, Enum):
    DEVELOPMENT = "development"
    DESIGN = "design"
    RESEARCH = "research"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    DOCUMENTATION = "documentation"
    GENERAL = "general"


class Deadline(str, Enum):
    MILESTONE = "milestone"
    RELEASE = "release"
    MEETING = "meeting"
    LAUNCH = "launch"
    FEEDBACK_DUE = "feedback_due"
    GENERAL = "general"


class Context(str, Enum):
    PROJECT = "project"
    SESSION = "session"
    USER_STATE = "user_state"
    ENVIRONMENT = "environment"
    GENERAL = "general"


class Observation(str, Enum):
    USER_BEHAVIOR = "user_behavior"
    SYSTEM_METRIC = "system_metric"
    INFERRED_PREFERENCE = "inferred_preference"
    ANOMALY = "anomaly"
    GENERAL = "general"
