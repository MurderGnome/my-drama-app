from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import requests
import urllib.parse
from bs4 import BeautifulSoup
import threading

MDL_BASE_URL = "https://microdramalist.com/api/v1"

class DramaApp(App):
    def build(self):
        self.title = "Drama & Cast Finder"
        
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Search Bar Row
        input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        self.search_input = TextInput(hint_text="Enter Drama Title...", multiline=False, font_size=16)
        search_btn = Button(text="Search", size_hint_x=0.3, background_color=(0.2, 0.6, 1, 1))
        search_btn.bind(on_press=self.start_search)
        
        input_layout.add_widget(self.search_input)
        input_layout.add_widget(search_btn)
        main_layout.add_widget(input_layout)
        
        # Scrollable Output Area
        scroll = ScrollView()
        self.result_label = Label(
            text="Enter a title above and tap Search.",
            size_hint_y=None,
            markup=True,
            font_size=15,
            halign='left',
            valign='top'
        )
        self.result_label.bind(texture_size=self.result_label.setter('size'))
        self.result_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        
        scroll.add_widget(self.result_label)
        main_layout.add_widget(scroll)
        
        return main_layout

    def start_search(self, instance):
        title = self.search_input.text.strip()
        if not title:
            self.result_label.text = "[color=ff0000]Please enter a drama title.[/color]"
            return
        
        self.result_label.text = "Searching..."
        threading.Thread(target=self.run_search, args=(title,), daemon=True).start()

    def run_search(self, title):
        try:
            search_res = requests.get(f"{MDL_BASE_URL}/search", params={"q": title}).json()
            if not search_res:
                Clock.schedule_once(lambda dt: self.update_results("[color=ff9900]No drama found with that title.[/color]"))
                return
            
            mdid = search_res[0]["id"]
            drama_details = requests.get(f"{MDL_BASE_URL}/dramas/{mdid}").json()
            
            d_title = drama_details.get("title", "Unknown Title")
            platforms = drama_details.get("availableOn", [])
            
            output = f"[b]Found:[/b] {d_title}\n\n[b]Available Platforms:[/b]\n"
            if platforms:
                for p in platforms:
                    name = p.get("name", "Platform")
                    url = p.get("url", "#")
                    output += f"• {name}: {url}\n"
            else:
                output += "No streaming platforms listed.\n"
            
            Clock.schedule_once(lambda dt: self.update_results(output))
        except Exception as e:
            err_msg = f"[color=ff0000]Error: {str(e)}[/color]"
            Clock.schedule_once(lambda dt: self.update_results(err_msg))

    def update_results(self, text):
        self.result_label.text = text

if __name__ == "__main__":
    DramaApp().run()
