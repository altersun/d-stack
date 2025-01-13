1. make and save local certs
2. Make directory / docker volume where certs live at runtime
3. local build
   1. Has it's own docker-compose?
   2. move local certs to live cert dir
   3. start sanic container then nginx container
4. Web build
   1. Has it's own docker-compose?
   2. start certbot container 
   3. Make live certs
   4. Move live certs to live cert dir
   5. Start sanic container then nginx container