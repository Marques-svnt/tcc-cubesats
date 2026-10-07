%
% =====================================================
% Classe ppgmc-uesc.cls
% Classe personalizada para teses e dissertações do PPGMC-UESC
% Baseada na classe abntex2 (ABNT)
%
% Autor: Valdex de Jesus Santos <valdexsantos@ifba.edu.br>
% Última atualização: 2026/04/17 - v7.0
% Site com templates: https://giveit.link/ProfValdexSantos
% =====================================================
\PassOptionsToPackage{inline,shortlabels}{enumitem} 
% Corrige conflito com listas personalizadas do abntex2

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{pacotes/ppgmc-uesc}[2026/04/17 v7.0]


% =====================================================
% PASSAGEM DE OPÇÕES PARA O ABNTeX2
% =====================================================

% Permite que o usuário passe opções diretamente para a classe (ex: 11pt, openany, etc.)
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{abntex2}}

% Opções padrão da classe
\PassOptionsToClass{
  12pt,           % Tamanho da fonte base
  openright,      % Capítulos iniciam em página ímpar
  a4paper,        % Papel A4
  sumario=tradicional,
  brazil          % Idioma principal (último sempre vence)
}{abntex2}

\ProcessOptions\relax
\LoadClass{abntex2}

\RequirePackage{chngcntr}
% Numerar equações de forma contínua (sem reiniciar por capítulo)
\counterwithout{equation}{chapter}

% =====================================================
% ESTILO DE PAGINAÇÃO E ELEMENTOS DO DOCUMENTO
% =====================================================

% -----------------------------------------------------
% 1. Elementos Pré-Textuais (capa, folha de rosto, etc.)
% -----------------------------------------------------
\renewcommand{\pretextual}{
  \pagenumbering{roman}                    % Contagem em romanos
  \setcounter{page}{1}                     % Folha de Rosto = página 1 (i)
  
  \aliaspagestyle{chapter}{empty}
  \pagestyle{empty}                        % Nenhum número visível
  \aliaspagestyle{cleared}{empty}
  \aliaspagestyle{part}{empty}
}

% -----------------------------------------------------
% 2. Elementos Textuais (a partir da Introdução)
%    - Numeração arábica visível
%    - Dá continuidade à contagem iniciada nos pré-textuais (de acordo com o manual da uesc)
% -----------------------------------------------------
\renewcommand{\textual}{
 \newcounter{tempPage}                    % Cria contador temporário
  \setcounter{tempPage}{\value{page}}      % Salva o número atual da página
  
  \pagenumbering{arabic}                   % Muda para arábico
  \setcounter{page}{\value{tempPage}}      % Restaura o número salvo (não reinicia em 1)
  
  % Escolhe estilo de cabeçalho conforme o tipo de documento
  \ifthenelse{\equal{\ABNTEXisarticle}{true}}{
    \pagestyle{plain}                      % Artigo: rodapé simples
  }{
    \pagestyle{abntheadings}               % Tese/Dissertação: cabeçalho ABNT
    \aliaspagestyle{chapter}{abntchapfirst}
  }
  
  \nouppercaseheads                        % Evita títulos em maiúsculas no cabeçalho
  \bookmarksetup{startatroot}              % Organiza bookmarks do PDF
}

% -----------------------------------------------------
% 3. Elementos Pós-Textuais (referências, apêndices, anexos)
% -----------------------------------------------------
\renewcommand{\postextual}{\phantompart}   % Evita página em branco desnecessária no final


%=====================================================
% COMANDOS DE DADOS DO DOCUMENTO
% =====================================================
% Esses comandos permitem preencher informações que aparecem na capa,
% folha de rosto e outros elementos pré-textuais.

% -----------------------------------------------------
% 1. Programa e Título
% -----------------------------------------------------
\providecommand{\imprimirprograma}{}
\newcommand{\programa}[1]{\renewcommand{\imprimirprograma}{#1}}

\providecommand{\imprimirsubtitulo}{}
\newcommand{\subtitulo}[1]{\renewcommand{\imprimirsubtitulo}{#1}}

\providecommand{\imprimirtitleenglish}{}
\newcommand{\titleenglish}[1]{\renewcommand{\imprimirtitleenglish}{#1}} % Título em inglês (opcional)

% -----------------------------------------------------
% 2. Orientador e Coorientador
% -----------------------------------------------------
\providecommand{\imprimirinstOrientador}{}
\newcommand{\instOrientador}[1]{\renewcommand{\imprimirinstOrientador}{#1}}

\providecommand{\imprimirinstCoorientador}{}
\newcommand{\instCoorientador}[1]{\renewcommand{\imprimirinstCoorientador}{#1}}

% -----------------------------------------------------
% 3. Área de Concentração e Linha de Pesquisa
% -----------------------------------------------------
\newcommand{\imprimirareaconcentracaoRotulo}{\'Area de concentra\c{c}\~ao: }
\providecommand{\imprimirareaconcentracao}{}
\newcommand{\areaconcentracao}[1]{\renewcommand{\imprimirareaconcentracao}{#1}}

\newcommand{\imprimirlinhapesquisaRotulo}{Linha de pesquisa: }
\providecommand{\imprimirlinhapesquisa}{}
\newcommand{\linhapesquisa}[1]{\renewcommand{\imprimirlinhapesquisa}{#1}}


% =====================================================
% DADOS DA DEFESA / BANCA EXAMINADORA
% =====================================================
% Comandos usados principalmente na folha de aprovação e ficha catalográfica

\providecommand{\imprimirdatadefesa}{}
\newcommand{\datadefesa}[1]{\renewcommand{\imprimirdatadefesa}{#1}}

\providecommand{\imprimirbancamembrointerno}{}
\newcommand{\bancamembrointerno}[1]{\renewcommand{\imprimirbancamembrointerno}{#1}}

\providecommand{\imprimirbancainstmembrointerno}{}
\newcommand{\bancainstmembrointerno}[1]{\renewcommand{\imprimirbancainstmembrointerno}{#1}}

\providecommand{\imprimirbancamembroexterno}{}
\newcommand{\bancamembroexterno}[1]{\renewcommand{\imprimirbancamembroexterno}{#1}}

\providecommand{\imprimirbancainstmembroexterno}{}
\newcommand{\bancainstmembroexterno}[1]{\renewcommand{\imprimirbancainstmembroexterno}{#1}}

% =====================================================
% LOGOTIPO DA INSTITUIÇÃO
% =====================================================
\newcommand{\logoInst}[1]{%
  \newcommand{\logo}{#1}%   % Define o comando \logo para usar na capa
}

% =====================================================
% OBJETOS FLUTUANTES (Figuras, Tabelas, Quadros, etc.)
% =====================================================
% Comando personalizado para notas em figuras/tabelas/quadros
\renewcommand{\nota}[1]{
  \begin{SingleSpacing}\par\end{SingleSpacing}
  \begin{tabular}{p{.05\textwidth}p{.9\textwidth}}
    Nota: & #1
  \end{tabular}
}

% =====================================================
% CONFIGURAÇÃO DE PARÁGRAFOS
% =====================================================
\setlength{\parindent}{1.3cm}   % Recuo da primeira linha
\setlength{\parskip}{0.2cm}     % Espaçamento entre parágrafos

% =====================================================
% REDEFINIÇÃO DE FONTES PARA TÍTULOS
% =====================================================
% Ajustes de fonte e estilo dos títulos (capítulos, seções, etc.)

\renewcommand{\ABNTEXchapterfont}{\normalfont\bfseries}
\renewcommand{\ABNTEXchapterfontsize}{\Large}

\renewcommand{\ABNTEXpartfont}{\normalfont}
\renewcommand{\ABNTEXpartfontsize}{\ABNTEXchapterfontsize}

\renewcommand{\ABNTEXsectionfont}{\normalfont}
\renewcommand{\ABNTEXsectionfontsize}{\Large}

\renewcommand{\ABNTEXsubsectionfont}{\normalfont}
\renewcommand{\ABNTEXsubsectionfontsize}{\large}

\renewcommand{\ABNTEXsubsubsectionfont}{\normalfont}
\renewcommand{\ABNTEXsubsubsectionfontsize}{\normalsize}

\renewcommand{\ABNTEXsubsubsubsectionfont}{\normalfont}
\renewcommand{\ABNTEXsubsubsubsectionfontsize}{\normalsize}


% =====================================================
% SUMÁRIO
% =====================================================
% Travessão no sumário para apêndices e anexos
\renewcommand{\cftchapteraftersnum}{\hfill{} -- \hfill{}}

% Espaçamento entre capítulos no sumário
\setlength{\cftbeforechapterskip}{1.0em \@plus\p@}

% =====================================================
% LISTAS PERSONALIZADAS
% =====================================================
% Nomes das listas (em português)
\addto\captionsbrazil{
  \renewcommand{\listadesiglasname}{Lista de abreviaturas e siglas}
  \renewcommand{\listadesimbolosname}{Lista de s\'imbolos}
  \renewcommand{\listfigurename}{Lista de figuras}
  \renewcommand{\listtablename}{Lista de tabelas}
  % Nomes para \autoref
  \renewcommand{\pageautorefname}{p\'agina}
  \renewcommand{\sectionautorefname}{Se{\c c}\~ao}
  \renewcommand{\subsectionautorefname}{Subse{\c c}\~ao}
  \renewcommand{\subsubsectionautorefname}{Subse{\c c}\~ao}
  \renewcommand{\paragraphautorefname}{Subse{\c c}\~ao}
}

% -------------------
% Lista de Quadros
% -------------------
\newcommand{\listofquadrosname}{Lista de quadros}
\newcommand{\quadroname}{Quadro}

\newfloat[chapter]{quadro}{loq}{\quadroname}
\newlistof{listofquadros}{loq}{\listofquadrosname}
\newlistentry{quadro}{loq}{0}
\counterwithout{quadro}{chapter}

\renewcommand{\cftquadroname}{\quadroname\space}
\renewcommand*{\cftquadroaftersnum}{\hfill--\hfill}

% =====================================================
% CAPA
% =====================================================
\makeatletter
\renewcommand{\imprimircapa}{
  \thispagestyle{empty}
  \setcounter{page}{0}   % Capa não entra na contagem de páginas
  
\begin{capa}
  \hspace{-2.0cm}
  \begin{minipage}{.2\textwidth}
    \logo
  \end{minipage}
  \quad
  \hspace{-1.5cm}
  \begin{minipage}{.9\textwidth}
    \begin{center}
      \normalfont\scshape\textbf{\imprimirinstituicao}\\\vspace*{0.3cm}
      \normalfont\scshape\textbf{\small\imprimirprograma}\\
      \abntex@ifnotempty{\imprimirareaconcentracao}{
        \normalfont\scshape{\imprimirareaconcentracao}
      }
    \end{center}
  \end{minipage}
  
  \vspace*{50pt}
  \begin{center}
    \large\normalfont\scshape\textbf\imprimirautor
  \end{center}
  
  \vspace*{170pt}
  \begin{center}
    \ABNTEXchapterfont\scshape\textbf\imprimirtitulo
    \abntex@ifnotempty{\imprimirsubtitulo}{
      {\ABNTEXchapterfont\scshape\textbf{\hspace*{-0.3em}: }}{\ABNTEXchapterfont\large\scshape\imprimirsubtitulo}
    }
  \end{center}
  
  \vspace*{\fill}
  \begin{center}
    \normalfont\scshape\textbf{\imprimirlocal}\\
    \normalfont\scshape\textbf{\imprimirdata}
  \end{center}
\end{capa}
}
\makeatother

% =====================================================
% FOLHA DE ROSTO
% =====================================================
\makeatletter
\renewcommand{\folhaderostocontent}{
  \thispagestyle{empty}
  \setcounter{page}{1}   % Folha de Rosto = página 1 (contada, mas invisível)
  
\begin{center}
  {\large\normalfont\scshape\textbf\imprimirautor}
\end{center}
\vspace*{150pt}
\begin{center}
  \ABNTEXchapterfont\Large\scshape\imprimirtitulo
  \abntex@ifnotempty{\imprimirsubtitulo}{
    {\ABNTEXchapterfont\Large\scshape{\hspace*{-0.3em}: }}{\ABNTEXchapterfont\large\scshape\imprimirsubtitulo}
  }
\end{center}
\vspace*{90pt}

\abntex@ifnotempty{\imprimirpreambulo}{
  \SingleSpacing
  \begin{tabular}{p{.25\textwidth}p{.13\textwidth}p{.44\textwidth}}
    & \multicolumn{2}{p{.6\textwidth}}{\small\hyphenpenalty=10000{\imprimirpreambulo}} \\ & & \\
    \abntex@ifnotempty{\imprimirareaconcentracao}{
      & \multicolumn{2}{p{.6\textwidth}}{\small\hyphenpenalty=10000{\imprimirareaconcentracaoRotulo\imprimirareaconcentracao}} \\ & & \\
    }
    \abntex@ifnotempty{\imprimirlinhapesquisa}{
      & \multicolumn{2}{p{.6\textwidth}}{\small\hyphenpenalty=10000{\imprimirlinhapesquisaRotulo\imprimirlinhapesquisa}} \\ & & \\
    }
    & \small\imprimirorientadorRotulo & \imprimirorientador \\
    & & \small\imprimirinstOrientador \\ & & \\
    \abntex@ifnotempty{\imprimircoorientador}{
      & \small\imprimircoorientadorRotulo & \imprimircoorientador \\
    }
  \end{tabular}
}
\vspace*{\fill}
\begin{center}
  \normalfont\scshape{\imprimirlocal}\\
  \normalfont\scshape{\imprimirdata}
\end{center}
}
\makeatother

% =====================================================
% DEDICATÓRIA E EPÍGRAFE
% =====================================================
\renewenvironment{dedicatoria}[1][]{
  \ifthenelse{\equal{#1}{}}{
    \PRIVATEbookmarkthis{\dedicatorianame}
  }{\pretextualchapter{#1}}
  \vspace*{\fill}
  \begin{flushright}
    \begin{minipage}{.5\textwidth}
      \begin{SingleSpacing}
        \setlength\parindent{0pt}
        \setlength\parskip{12pt}
  }{
      \end{SingleSpacing}
    \end{minipage}
  \end{flushright}
}

\renewenvironment{epigrafe}[1][]{
  \ifthenelse{\equal{#1}{}}{
    \PRIVATEbookmarkthis{\epigraphname}
  }{\pretextualchapter{#1}}
  \vspace*{\fill}
  \begin{flushright}
    \begin{minipage}{.5\textwidth}
      \begin{SingleSpacing}
        \setlength\parindent{0pt}
        \setlength\parskip{12pt}
  }{
      \end{SingleSpacing}
    \end{minipage}
  \end{flushright}
}

% =====================================================
% IMPORTAÇÃO DE PACOTES
% =====================================================
\usepackage[abnt-repeated-author-omit=yes,
            abnt-nbr10520=1988,
            alf,
            abnt-etal-cite=3,
            abnt-etal-list=0,
            abnt-etal-text=it,
            bibjustif,
            abnt-url-package=url,
            abnt-emphasize=bf,
            abnt-and-type=e,
            abnt-doi=doi]{abntex2cite}

\usepackage{bookmark}          % Bookmarks no PDF
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{graphicx}
\usepackage{float}             % Permite [H] em figuras
\usepackage{amsfonts, amssymb, amsmath}
\usepackage{cancel}
\usepackage{lastpage}
\usepackage{verbatim}
\usepackage{multirow, array}
\usepackage{indentfirst}
\usepackage[algoruled, portuguese]{algorithm2e}
\usepackage{caption}
\usepackage{subcaption}
\usepackage{hyperref}
\usepackage{multicol}
\usepackage{xcolor, colortbl}
\usepackage{pdfpages}
\usepackage{pdflscape}

% =====================================================
% CONFIGURAÇÃO DO HYPERREF (PDF)
% =====================================================
\makeatletter
\hypersetup{
  portuguese,
  colorlinks=true,
  linkcolor=blue,
  citecolor=blue,
  filecolor=blue,
  urlcolor=blue,
  breaklinks=true,
  pdftitle={\@title},
  pdfauthor={\@author},
  pdfsubject={\imprimirpreambulo},
  pdfkeywords={ABNT, LaTeX, abntex2, UESC, PPGMC}
}