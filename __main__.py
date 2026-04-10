import sys
import game

def main() -> None:
	game.init(sys.argv[1] if len(sys.argv) > 1 else None)
	game.run()

if __name__ == "__main__":
	main()
