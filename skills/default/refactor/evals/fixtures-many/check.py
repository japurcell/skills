import fields


for convert in (fields.page_size, fields.request_page_size):
    assert convert(0) == 1
    assert convert(12) == 12
    assert convert(110) == 100

for convert in (fields.slug, fields.article_slug):
    assert convert(' New  Page ') == 'new-page'
    assert convert('') == ''

for convert in (fields.suffix, fields.upload_suffix):
    assert convert('a.PDF') == 'pdf'
    assert convert('noext') == 'noext'

for convert in (fields.priority, fields.queue_priority):
    assert convert(' urgent ') == True
    assert convert('normal') == False

for convert in (fields.minutes, fields.duration_minutes):
    assert convert(0) == 0
    assert convert(61) == 2
