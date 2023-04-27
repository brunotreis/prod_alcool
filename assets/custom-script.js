alert('Esse app web foi criado apenas para fins didáticos! ')
alert('Site pouco responsivo, abrir preferencialmente no Computador!')
senha = '123456';
senhadig = prompt("Digite a senha","")
if (senha != senhadig){
alert('Acesso negado!');
top.location.href='erro.htm';
}