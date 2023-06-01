# Run a code formatter.
all:
	@black --line-length 79 --preview --quiet .
