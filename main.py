from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.core.window import Window
import sqlite3
# Import abaixo cancela a msg Error in sys.excepthook causado
# ao modificar os itens do cache no recycleview
from kivy.uix.recycleview.views import _cached_views, _view_base_cache

Window.clearcolor = (1,1,1,1)

kvcode = """
#: import C kivy.utils.get_color_from_hex
<TextInput@TextInput>:
	multiline: False
	write_tab: False
	halign: 'center'

<Label@Label>:
	color: C("1E90FF")
	
<MeuLayout>:
	orientation: 'horizontal'
	
	lbl1: 'lbl_um'
	lbl2: 'lbl_dois'
	
	Label:
		id: lbl_um
		text: root.lbl1
	
	Label:
		id: lbl_dois
		text: root.lbl2
		
	Button:
		id: btn_deletar
		text: "DEL"
		size_hint_x: .28
		on_press: root.parent.parent.parent.parent.deletar(root.lbl1, root.lbl2)
		
TelaPrincipal:

	orientation: 'vertical'
	
	Label:
		text: "PILOTOS F1 2020"
		color: C("0B0101")
		size_hint_y: .1
		
	BoxLayout:
		size_hint_y: .05
		
		Label:
			text: "PILOTO"
			color: C("0B0101")
		Label:
			text: "EQUIPE"
			color: C("0B0101")
		Label:
			size_hint_x: .28
			text: "EXCLUIR"
			color: C("0B0101")
		
	ScrollView:
		RecycleView:
			id: rv
			data: [{'lbl1': piloto, 'lbl2': equipe} for piloto, equipe in root.dados]
			viewclass: 'MeuLayout'
			RecycleBoxLayout:
				default_size: None, dp(56)
				default_size_hint: 1, None
				size_hint_y: None
				height: self.minimum_height
				orientation: 'vertical'
				
	BoxLayout:
		size_hint_y: .1
		TextInput:
			id: txt_piloto
			hint_text: "Piloto"
			
		TextInput:
			id: txt_equipe
			hint_text: "Equipe"
			
		Button:
			text: "Add/Editar"
			size_hint_x: .28
			on_press: root.adicionar(root.ids.txt_piloto.text, root.ids.txt_equipe.text)
				
"""

# BANCO DE DADOS
class Login(object):
	def __init__(self, database):
		self.conectado = False
		self._db = database
		self._conn = sqlite3.connect(database)

	def BuscarTudo(self):
		cursor = self._conn.execute("SELECT * from Nomes")
		description = list()
		for linha in cursor:
			pessoa = dict()
			for i, coluna in enumerate(linha):
				pessoa[cursor.description[i][0]] = coluna
			description.append(pessoa)
		return description

	def NovoRegistro(self, piloto, equipe):
		if not self.ChecarNome(piloto):
			self._conn.execute("""
			INSERT INTO Nomes (piloto, equipe)
			VALUES (?, ?)""", (piloto, equipe))
			self._conn.commit()
			return True
		else:
			return False

	def DeletarRegistro(self, piloto):
		self._conn.execute("DELETE FROM Nomes WHERE piloto=?", (piloto,))
		self._conn.commit()
		return True
			
	def EditarRegistro(self, piloto, equipe):
		cursor = self._conn.execute('SELECT piloto, equipe from Nomes')
		for row in cursor: 
			if row[0] == piloto:
				self._conn.execute("UPDATE Nomes SET equipe = ? WHERE piloto = ?", (equipe,piloto))
				self._conn.commit()
				return True
			
	def ChecarNome(self, piloto):
		cursor = self._conn.execute('SELECT piloto from Nomes')
		for row in cursor:
			if row[0] == piloto:
				print(piloto, "ja existe.")
				return True
		return False
		
banco = Login("banco.db")

class TelaPrincipal(BoxLayout):
	
	dados = ListProperty()
	
	def __init__(self, *args, **kwargs):
		super(TelaPrincipal, self).__init__(*args, **kwargs)
		self.popular_rv()
		

	def popular_rv(self):
	
		self.dados = []
		descricoes = banco.BuscarTudo()
		for item in descricoes:
			self.dados.append([item['piloto'], item['equipe']])

		
	def adicionar(self, piloto, equipe):
	
		status = banco.NovoRegistro(piloto, equipe)
		if status == True:
			self.popular_rv()
			self.ids.txt_piloto.text = ""
			self.ids.txt_equipe.text = ""
		else:
			self.editar(piloto, equipe)
		
		
	def deletar(self, piloto, equipe):
	
		status = banco.DeletarRegistro(piloto)
		if status == True:
			self.popular_rv()

		
	def editar(self, piloto, equipe):
	
		status = banco.EditarRegistro(piloto, equipe)
		if status == True:
			self.popular_rv()
	
		
class MeuLayout(BoxLayout):
	pass
		
''' APP CLASS '''
class Aplicativo(App):

	def build(self):
		main_widget = Builder.load_string(kvcode)
		return main_widget

if __name__ == '__main__':
	Aplicativo().run()