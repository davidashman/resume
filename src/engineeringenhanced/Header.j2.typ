{% macro image() %}
#pad(left: {{ design.header.photo_space_left|default('0.4cm') }}, right: {{ design.header.photo_space_right|default('0.4cm') }}, image("{{ cv.photo.name }}", width: {{ design.header.photo_width }}))
{% endmacro %}

{% if cv.photo %}
{% set photo = "image(\"" + cv.photo|string + "\", width: "+ design.header.photo_width + ")" %}
#grid(
{% if design.header.photo_position|default('right') == "left" %}
  columns: (auto, 1fr),
{% else %}
  columns: (1fr, auto),
{% endif %}
  column-gutter: 0cm,
  align: horizon + left,
{% if design.header.photo_position|default('right') == "left" %}
  [{{ image() }}],
  [
{% else %}
  [
{% endif %}
{% endif %}
{% if cv.name %}
= {{ cv.name }}
{% endif %}

#connections(
{% for connection in cv.connections %}
  [{{ connection }}],
{% endfor %}
)

{% if cv.summary %}
#set text(size: 0.9em)
{{ cv.summary }}

{% endif %}
{% if cv.photo %}
{% if design.header.photo_position|default('right') == "left" %}
  ]
)
{% else %}
  ],
  [{{ image() }}],
)
{% endif %}
{% endif %}
