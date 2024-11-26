<h1>Sistema de Marcação de Pontos</h1>

Um aplicativo web projetado para simplificar a marcação e o acompanhamento de pontos dos colaboradores de uma empresa.  
O sistema conta com uma interface intuitiva e de fácil utilização, permitindo que os funcionários registrem suas entradas e saídas de maneira prática,  
sem comprometer suas demandas ou a eficiência no trabalho.

<h3>📋 Funcionalidades</h3>
<ul>
<li>Registro de ponto (entrada, saída e intervalos).</li>
<li>Autenticação: Login seguro utilizando o sistema de usuários do Django</li>
<li>Gerenciamento de usuários: Diferenciação entre perfis de colaboradores e administradores.</li>
<li>Painel administrativo para gerenciar usuários e registros.</li>
<li>Painel administrativo: Visualização e edição de dados por administradores.</li>
<li>Exportação de relatórios para sua planilha online (gsheets)</li>
</ul>
<h3>🚀 Tecnologias Utilizadas</h3>
<ul>
<li>Frontend: HTML, Bootstrap, CSS e JS.</li>
<li>Backend: Python.</li>
<li>Framework Web: Django.</li>
<li>Banco de Dados: SQLite 3 (fácil adaptação para PostegreSQL).</li>
<li>Autenticação: Libs Django auth.</li>
<li>Hospedagem: Fly.io.</li>
</ul>
<h3>✅Instalação</h3>
<ol>
	<li>Clone o repositório:</li>
	<ul>
		<li>git clone https://github.com/iTzKoringaF4/rp_loggi.git</li>
		<li>cd nome-do-repositorio</li>
	</ul>
	<li>Crie um ambiente virtual:</li>
 <ul>
		<li>python -m venv venv<br>
		<li><b>Para Linux/Macsource</b> venv/bin/activate</li>
		<li><b>Para Windows</b> venv\Scripts\activate</li>
 </ul>
		<li>Instale as dependências:</li>
	<ul>
		<li>pip install -r requirements.txt</li>
	</ul>
	<li>Realize as migrações do banco de dados:</li>
	<ul>
		<li>python manage.py makemigrations</li>
		<li>python manage.py migrate</li>
 </ul>
	<li>Inicie o servidor de desenvolvimento:</li>
	<ul>
		<li>python manage.py runserver</li>
	</ul>
</ol>
<h3>Contato</h3>
<ul>
<li>Autor: Johnatas B.E</li>
<li>Email: johnataseugenio@gmail.com</li>
<li>GitHub: </li>
</ul>

