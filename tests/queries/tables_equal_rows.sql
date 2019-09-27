-- Do a set difference from both sides
SELECT * FROM
(
    SELECT * FROM {{ table }}
    EXCEPT
    SELECT * FROM {{ other_table }}
)

UNION ALL

SELECT * FROM
(
    SELECT * FROM {{ other_table }}
    EXCEPT
    SELECT * FROM {{ table }}
)
