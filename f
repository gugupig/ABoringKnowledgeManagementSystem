[0;1;31m×[0m mongod.service - MongoDB Database Server
     Loaded: loaded (/lib/systemd/system/mongod.service; disabled; vendor preset: enabled)
     Active: [0;1;31mfailed[0m (Result: exit-code) since Tue 2024-01-30 05:45:19 CET; 10s ago
       Docs: https://docs.mongodb.org/manual
    Process: 10700 ExecStart=/usr/bin/mongod --config /etc/mongod.conf [0;1;31m(code=exited, status=14)[0m
   Main PID: 10700 (code=exited, status=14)
        CPU: 46ms

Jan 30 05:45:19 vmi611223.contaboserver.net systemd[1]: Started MongoDB Database Server.
Jan 30 05:45:19 vmi611223.contaboserver.net systemd[1]: [0;1;39m[0;1;31m[0;1;39mmongod.service: Main process exited, code=exited, status=14/n/a[0m
Jan 30 05:45:19 vmi611223.contaboserver.net systemd[1]: [0;1;38;5;185m[0;1;39m[0;1;38;5;185mmongod.service: Failed with result 'exit-code'.[0m
