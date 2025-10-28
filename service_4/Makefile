up:
	@docker run --rm --name service_4_ch clickhouse/clickhouse-server:25.7-alpine

down:
	@docker stop service_4_ch

init:
	@docker exec -i service_4_ch clickhouse-client --multiquery < ./add_todays.sql

sh:
	@docker exec -it service_4_ch clickhouse-client
