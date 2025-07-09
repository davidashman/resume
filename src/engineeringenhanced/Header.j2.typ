((* if cv.photo *))
#two-col(
  right-column-width: design-header-photo-width * 1.1,
  left-column-width: 1fr,
  column-gutter: 0.7em,
  right-content: [
    #align(
      right + horizon,
      box(
        clip: true,
        radius: design-header-photo-width / 2,
        width: design-header-photo-width,
        height: design-header-photo-width,
        image("profile_picture.jpg", width: design-header-photo-width)
      )
    )
  ],
  left-content: [
    #set align(left + horizon)
((* endif *))
((* if cv.name *))
= <<cv.name|escape_typst_characters>>
((* endif *))

// Print connections:
#let connections-list = (
((* for connection in cv.connections *))
  [((*- if connection["url"] -*))
  #box(original-link("<<connection["url"]>>")[
  ((*- endif -*))
  ((*- if design.header.use_icons_for_connections -*))
    #fa-icon("<<connection["typst_icon"]>>", size: 1em) #h(0.05cm)
  ((*- endif -*))
  ((*- if not design.header.use_urls_as_placeholders_for_connections or not connection["url"] -*))
    <<connection["placeholder"]|escape_typst_characters>>
  ((*- else -*))
    <<connection["clean_url"]|escape_typst_characters>>
  ((*- endif -*))
  ((*- if connection["url"] -*))
  ])
  ((*- endif -*))],
((* endfor *))
)
#connections(connections-list)

((* if cv.summary *))
#set text(size: 1em, fill: design-colors-connections, font: design-header-connections-font-family, style: "italic")
#box(
  "<<cv.summary|escape_typst_characters>>"
)
((* endif *))
((* if cv.photo *))
    #v(0.5em)
  ],
)
((* endif *))
#v(-0.5em)
