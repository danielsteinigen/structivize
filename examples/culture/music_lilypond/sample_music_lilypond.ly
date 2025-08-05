\header {tagline = ""}
\version "2.24.2"

melody = \relative c' {
  \key c \major
  \time 4/4
  c4 e g a
  g4 f e d
  c2 r2
}

octaveDoubled = \relative c'' {
  \key c \major
  \time 4/4
  c4 e g a
  g4 f e d
  c2 r2
}

\score {
  <<
    \new Staff = "Melody" <<
      \set Staff.instrumentName = #"Melody"
      \melody
    >>
    \new Staff = "Octave Double" <<
      \set Staff.instrumentName = #"Octave Double"
      \octaveDoubled
    >>
  >>
  \layout { }
  \midi { }
}
