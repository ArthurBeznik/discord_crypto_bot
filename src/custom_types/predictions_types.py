# predictions_types.py

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Tuple

# prediction = (prediction_id, user_id, crypto, prediction_date, predicted_price, actual_price, accuracy)
# ? Type for a single prediction
PredictionType = Tuple[int, int, str, datetime, Decimal, Decimal, Decimal]

# predictions: [
#     (
#         34,
#         243051996200828929,
#         "bitcoin",
#         datetime.date(2024, 9, 18),
#         Decimal("61000.00000000"),
#     ),
#     (
#         67,
#         522413467668578313,
#         "bitcoin",
#         datetime.date(2024, 9, 24),
#         Decimal("100.00000000"),
#     ),
#     (
#         101,
#         522413467668578313,
#         "ethereum",
#         datetime.date(2024, 9, 24),
#         Decimal("100.00000000"),
#     ),
# ]
# ? Type for all predictions
AllPredictionsType = List[PredictionType]

# score = [crypto, predicted_price, actual_price, accuracy, predicted_date]
# ? Type for a single score
ScoreType = Tuple[str, Decimal, float, Decimal, datetime]

# user_scores = (user_score_1, user_score_2)
# ? Type for a single user's scores
UserScoresType = List[ScoreType]

# user_scores: {
#     243051996200828929: [
#         (
#             "bitcoin",
#             Decimal("61000.00000000"),
#             60317.0319794625,
#             Decimal("0.9886770287243237936895138413"),
#             datetime.date(2024, 9, 18),
#         )
#     ],
#     522413467668578313: [
#         (
#             "bitcoin",
#             Decimal("100.00000000"),
#             63327.02654450202,
#             Decimal("0.0015791046170425616855354897"),
#             datetime.date(2024, 9, 24),
#         ),
#         (
#             "ethereum",
#             Decimal("100.00000000"),
#             2647.9931622033255,
#             Decimal("0.0377644479703990736336902052"),
#             datetime.date(2024, 9, 24),
#         ),
#     ],
# }
# all_users_scores = {user_id_1: [user_score_1, user_score_2], user_id_2: [user_score_1, ...]}
# ? Type for all users' scores
AllUsersScoresType = Dict[int, UserScoresType]

# user_avg_accuracy: {
#     243051996200828929: Decimal("0.9886770287243237936895138413"),
#     522413467668578313: Decimal("0.0377644479703990736336902052"),
# }
# user_avg_accuracy = {user_id_1: accuracy, user_id_2: accuracy, ...}
# ? Type for all users average accuracy
AllUsersAverageAccuracyType = Dict[int, Decimal]

# ? Type for leaderboard
LeaderboardType = List[Tuple[int, float]]

# leaderboard_data: [
#     (
#         243051996200828929,
#         (
#             "bitcoin",
#             Decimal("61000.00000000"),
#             60317.0319794625,
#             Decimal("0.9886770287243237936895138413"),
#             datetime.date(2024, 9, 18),
#         ),
#     ),
#     (
#         522413467668578313,
#         (
#             "polkadot",
#             Decimal("4.00000000"),
#             4.320743598373926,
#             Decimal("0.9257665744168122346466570478"),
#             datetime.date(2024, 10, 23),
#         ),
#     ),
#     (
#         522413467668578313,
#         (
#             "ethereum",
#             Decimal("100.00000000"),
#             2647.9931622033255,
#             Decimal("0.0377644479703990736336902052"),
#             datetime.date(2024, 9, 24),
#         ),
#     ),
#     (
#         522413467668578313,
#         (
#             "ethereum",
#             Decimal("9999.00000000"),
#             2618.3298618964914,
#             Decimal("-1.818846565328323629039447005"),
#             datetime.date(2024, 1, 12),
#         ),
#     ),
# ]
# [(user_id_1, (prediction_1)), (user_id_2, (prediction_1)), ...]
LeaderboardDataType = List[Tuple[int, Tuple[str, float, float, float, datetime]]]
