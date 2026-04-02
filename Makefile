include .env

clean_inputs:
	find inputs/* -type f ! -name '.gitkeep' -delete
clean_outputs:
	find outputs/* -type f ! -name '.gitkeep' -delete

local_server_docker: 
	docker compose up --build

local_server:
	streamlit run app.py --server.headless true
