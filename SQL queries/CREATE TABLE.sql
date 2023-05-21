CREATE TABLE Usuarios(
	idUsuario		INTEGER IDENTITY(1,1),
	nome			VARCHAR(60) NOT NULL,
	username		VARCHAR(15) NOT NULL,
	senha			VARCHAR(15) NOT NULL,
	ic_admin		BIT NOT NULL DEFAULT 0,
	CONSTRAINT pk_tb_usuarios_idUsuario	PRIMARY KEY(idUsuario)
);

CREATE TABLE Aulas(
	idAula			INTEGER IDENTITY(1,1),
	nome			VARCHAR(60) NOT NULL,
	descricao		VARCHAR(3000),
	data			DATE NOT NULL,
	horaInicio		TIME NOT NULL,
	horaTermino		TIME NOT NULL,
	CONSTRAINT pk_tb_aulas_idAula PRIMARY KEY(idAula)
);



CREATE TABLE AulasUsuarios(
	idAluno				INTEGER,
	idProfessor			INTEGER,
	idAula				INTEGER,
	CONSTRAINT pk_tb_aulasUsuarios_idAluno_idProfessor_idAula PRIMARY KEY(idAluno, idProfessor,idAula),
	CONSTRAINT fk_tb_aulasUsuarios_idAluno FOREIGN KEY(idAluno) REFERENCES Usuarios(idUsuario),
	CONSTRAINT fk_tb_aulasUsuarios_idProfessor FOREIGN KEY(idProfessor) REFERENCES Usuarios(idUsuario),
	CONSTRAINT fk_tb_aulasUsuarios_idAula	FOREIGN KEY(idAula) REFERENCES Aulas(idAula)

);

