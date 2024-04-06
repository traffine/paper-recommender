resource "aws_dynamodb_table" "chat" {
  name           = "${var.app_name}-chat"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "chat_id"
  range_key      = "timestamp"
  stream_enabled = false

  point_in_time_recovery {
    enabled = false
  }

  attribute {
    name = "chat_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  global_secondary_index {
    name            = "UserIdIndex"
    hash_key        = "user_id"
    projection_type = "ALL"
  }
}
