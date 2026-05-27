#!/bin/bash
set -e

user=postgres
db=db

PSQL="psql -U "$user" -d "$db" -h localhost -t -A -q"

print() { echo -e "\n=== $1 ==="; }

print "Задание 1.1: calc_arrival_time_valekzhanin"
$PSQL -c "SELECT pg_get_functiondef(oid) FROM pg_proc WHERE proname = 'calc_arrival_time_valekzhanin' AND pronamespace = 'public'::regnamespace;"

print "Задание 1.2: is_trip_today_valekzhanin"
$PSQL -c "SELECT pg_get_functiondef(oid) FROM pg_proc WHERE proname = 'is_trip_today_valekzhanin' AND pronamespace = 'public'::regnamespace;"

print "Задание 1.3: format_fio_valekzhanin"
$PSQL -c "SELECT pg_get_functiondef(oid) FROM pg_proc WHERE proname = 'format_fio_valekzhanin' AND pronamespace = 'public'::regnamespace;"

print "Задание 2.1: get_driver_schedule_valekzhanin"
$PSQL -c "SELECT pg_get_functiondef(oid) FROM pg_proc WHERE proname = 'get_driver_schedule_valekzhanin' AND pronamespace = 'public'::regnamespace;"

print "Задание 2.2: check_driver_violations_valekzhanin"
$PSQL -c "SELECT pg_get_functiondef(oid) FROM pg_proc WHERE proname = 'check_driver_violations_valekzhanin' AND pronamespace = 'public'::regnamespace;"

print "Задание 2.3: calc_month_cost_valekzhanin"
$PSQL -c "SELECT pg_get_functiondef(oid) FROM pg_proc WHERE proname = 'calc_month_cost_valekzhanin' AND pronamespace = 'public'::regnamespace;"

print "Задание 3.1: Триггер проверки билетов"
$PSQL -c "SELECT pg_get_triggerdef(oid) FROM pg_trigger WHERE tgname = 'trg_check_tickets' AND NOT tgisinternal;"
$PSQL -c "SELECT pg_get_functiondef(oid) FROM pg_proc WHERE proname = 'fn_check_ticket_limit_valekzhanin' AND pronamespace = 'public'::regnamespace;"

print "Задание 3.2: Триггер валидации маршрутов"
$PSQL -c "SELECT pg_get_triggerdef(oid) FROM pg_trigger WHERE tgname = 'trg_validate_route' AND NOT tgisinternal;"
$PSQL -c "SELECT pg_get_functiondef(oid) FROM pg_proc WHERE proname = 'fn_validate_route_valekzhanin' AND pronamespace = 'public'::regnamespace;"

print "Задание 3.3: Триггер архивации рейсов"
$PSQL -c "SELECT pg_get_triggerdef(oid) FROM pg_trigger WHERE tgname = 'trg_archive_trip' AND NOT tgisinternal;"
$PSQL -c "SELECT pg_get_functiondef(oid) FROM pg_proc WHERE proname = 'fn_archive_trip_valekzhanin' AND pronamespace = 'public'::regnamespace;"

echo -e "\nВывод завершен."
