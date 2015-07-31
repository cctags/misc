default: $(shell uname -s)

Linux: ipv6_test

ipv6_test: main.c
	@echo Compiling $< ..
	@gcc -Wall $< -o $@

windows32: ipv6_test.exe

ipv6_test.exe: main.c
	@echo Compiling $< ..
	@gcc.exe -Wall $< -o $@ -lwsock32 -lws2_32
