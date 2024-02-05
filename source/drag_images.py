import sublime, sublime_plugin

class GrabImagesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print ("xxxxxxxxxx")
        self._edit = edit
        filenames = self._gather_images()
        results = ["image::{}[]".format(f) for f in filenames]
        self._replace_selected_text(results)
        self._unselect()

    def _replace_selected_text(self, doc):
        if type(doc) is list:
            doc = "\n".join(doc)
        doc += "\n"
        self.view.replace(self._edit, self.view.sel()[0], doc)

    def _unselect(self):
        s = self.view.sel()
        pt = s[0].end()
        s.clear()
        s.add(sublime.Region(pt,pt))

    def _gather_images(self) -> list:
        results = []
        for sheet in self.view.window().sheets():
            if (type(sheet) is sublime.ImageSheet):
                results.append(sheet.file_name())
                sheet.close()
        return results
