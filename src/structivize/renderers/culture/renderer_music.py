import re

from ...renderer import Renderer


class RendererMusic(Renderer):

    def _replace_tagline(self, path):
        with open(path, "r") as file:
            content = file.read()
        content = re.sub(r'tagline\s*=\s*".*?"', 'tagline = ""', content)
        with open(path, "w") as file:
            file.write(content)

    def _conv_abc2ly(self, filepath_code, filepath_img):
        self._execute_process(commands=["abc2ly", "-o", f"{filepath_img}.ly", filepath_code])

    def _conv_xml2ly(self, filepath_code, filepath_img):
        self._execute_process(commands=["musicxml2ly", "-o", f"{filepath_img}", filepath_code])

    def _conv_ly2svg(self, filepath_code, filepath_img):
        self._execute_process(
            commands=["lilypond", "-dno-point-and-click", "-dresolution=300", "-f", "svg", "-o", filepath_img, filepath_code]
        )
        self._svg_save(filepath_img)
        # other implementation for cropping: add '#(ly:set-option 'crop #t)' to .ly

    def _hex_to_lilypond_color(self, hex_str):
        hex_str = hex_str.lstrip('#')
        r = int(hex_str[0:2], 16) / 255.0
        g = int(hex_str[2:4], 16) / 255.0
        b = int(hex_str[4:6], 16) / 255.0
        return f"#(rgb-color {r:.2f} {g:.2f} {b:.2f})"
    
    def _apply_styling(self, filepath_img, config):

        c_note  = self._hex_to_lilypond_color(config.get("note_color", "#000000"))
        c_staff = self._hex_to_lilypond_color(config.get("staff_color", "#000000"))
        c_time  = self._hex_to_lilypond_color(config.get("time_color", "#000000"))
        
        shape = config.get("note_shape", "default")
        thick = config.get("thickness", 1.0)
        size  = config.get("staff_size", 20)

        overrides = f"""
        #(layout-set-staff-size {size})
        \\context {{
            \\Voice
            \\override NoteHead.color = {c_note}
            \\override NoteHead.style = #'{shape}
            \\override Stem.color = {c_note}
            \\override Stem.thickness = #{1.3 * thick}
            \\override Beam.color = {c_note}
            \\override Beam.beam-thickness = #{0.48 * thick}
            \\override Accidental.color = {c_note}
        }}
        \\context {{
            \\Staff
            \\override StaffSymbol.color = {c_staff}
            \\override StaffSymbol.thickness = #{1.0 * thick}
            \\override Clef.color = {c_time}
            \\override TimeSignature.color = {c_time}
            \\override KeySignature.color = {c_time}
            \\override BarLine.color = {c_staff}
            \\override BarLine.hair-thickness = #{1.6 * thick}
        }}
        """
        
        with open(f"{self.filepath_image}.ly", "r") as f:
            content = f.read()

        if "\\layout" in content:
            content = re.sub(
                r'(\\layout\s*\{)', 
                lambda m: f"{m.group(1)}\n{overrides}", 
                content, 
                count=1
            )
        else:
            fallback_block = f"\\layout {{\n{overrides}\n}}"
            if "\\midi" in content:
                content = content.replace("\\midi", fallback_block + "\n\\midi")
            else:
                content += fallback_block

        content = f"#(set-global-staff-size {size})\n" + content

        with open(f"{self.filepath_image}.ly", "w") as f:
            f.write(content)