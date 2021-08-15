build/book.pdf: *.asciidoc
	asciidoctor-pdf -vwt -b pdf -d book -o build/book.pdf book.asciidoc

clean:
	rm build/*

all: build/book.pdf
