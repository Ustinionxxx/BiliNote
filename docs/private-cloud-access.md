# Private cloud access

The Compose web port listens on the server loopback interface. Use an SSH tunnel to access the frontend, API, uploads and screenshots. This prevents unauthenticated Internet clients from changing providers or triggering paid model requests. The backend and frontend containers have no published host ports.

For a server whose APP_PORT is 3015:

```sh
ssh -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 \
  -L 127.0.0.1:4315:127.0.0.1:3015 user@server
```

Open http://127.0.0.1:4315 in the same computer's browser. Keep the SSH connection running. Replace the remote port with the server's APP_PORT value when different; use your normal SSH identity options. Each device needs its own authorized SSH connection. Do not restore a wildcard port binding to enable remote access. Public browser access needs a separate authenticated HTTPS gateway.

Provider list and detail responses mask API keys. Backend model calls retain access to the stored key. Saving an unchanged masked value does not replace the stored key. Provider updates do not print credential fields or exception contents.

After fixing an exposed deployment, revoke any exposed keys at their providers before storing replacements. Masking a response cannot invalidate an already copied key. Existing application data is preserved.
