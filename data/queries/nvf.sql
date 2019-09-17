-- Credentials: eusopdw

SELECT org, warehouse, metric_date, value
FROM daily.d_sop_network_viewer_actuals
WHERE
  metric_name = 'New Vendor Freight'
  AND current_flag = 1
  AND metric_date between '{start}' and '{end}'
  AND warehouse not in (
    '3PL',
    'Amazon Network',
    'HeavyBulky',
    'Mix',
    'MixedSortability',
    'Non Sortable',
    'NonSortable',
    'Others',
    'Pantry',
    'Sortable',
    'Sortable DE'
  )
