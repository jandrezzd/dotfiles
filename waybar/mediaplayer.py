#!/usr/bin/env python3
import argparse
import logging
import sys
import signal
import gi
import json
gi.require_version('Playerctl', '2.0')
from gi.repository import Playerctl, GLib

logger = logging.getLogger(__name__)

# Variables globales para el manejo limpio de recursos
loop = None
manager = None
players = []

def write_output(text, player):
    logger.info('Writing output')

    output = {'text': text,
              'class': 'custom-' + player.props.player_name,
              'alt': player.props.player_name}

    sys.stdout.write(json.dumps(output) + '\n')
    sys.stdout.flush()


def on_play(player, status, manager):
    logger.info('Received new playback status')
    on_metadata(player, player.props.metadata, manager)


def on_metadata(player, metadata, manager):
    logger.info('Received new metadata')
    track_info = ''

    if player.props.player_name == 'spotify' and \
            'mpris:trackid' in metadata.keys() and \
            ':ad:' in player.props.metadata['mpris:trackid']:
        track_info = 'AD PLAYING'
    elif player.get_artist() != '' and player.get_title() != '':
        track_info = '{artist} - {title}'.format(artist=player.get_artist(),
                                                 title=player.get_title())
    else:
        track_info = player.get_title()

    if player.props.status != 'Playing' and track_info:
        track_info = '⏸ ' + track_info
    write_output(track_info, player)


def on_player_appeared(manager, player, selected_player=None):
    if player is not None and (selected_player is None or player.name == selected_player):
        init_player(manager, player)
    else:
        logger.debug("New player appeared, but it's not the selected player, skipping")


def on_player_vanished(manager, player):
    logger.info('Player has vanished')
    # Remover el player de la lista de players activos
    global players
    if player in players:
        players.remove(player)
    
    sys.stdout.write('\n')
    sys.stdout.flush()


def init_player(manager, name):
    logger.debug('Initialize player: {player}'.format(player=name.name))
    player = Playerctl.Player.new_from_name(name)
    player.connect('playback-status', on_play, manager)
    player.connect('metadata', on_metadata, manager)
    manager.manage_player(player)
    
    # Agregar a la lista de players activos
    global players
    players.append(player)
    
    on_metadata(player, player.props.metadata, manager)


def cleanup_resources():
    """Limpia todos los recursos antes de salir"""
    logger.debug('Cleaning up resources')
    
    global players, manager
    
    # Desconectar todos los players
    for player in players:
        try:
            # Desconectar señales
            player.disconnect_by_func(on_play)
            player.disconnect_by_func(on_metadata)
        except Exception as e:
            logger.warning(f'Error disconnecting player signals: {e}')
    
    players.clear()
    
    # Si el manager existe, intentar limpiarlo
    if manager:
        try:
            manager.disconnect_by_func(on_player_appeared)
            manager.disconnect_by_func(on_player_vanished)
        except Exception as e:
            logger.warning(f'Error disconnecting manager signals: {e}')


def signal_handler(sig, frame):
    logger.debug('Received signal to stop, exiting')
    
    # Limpiar recursos
    cleanup_resources()
    
    sys.stdout.write('\n')
    sys.stdout.flush()
    
    # Detener el loop correctamente
    global loop
    if loop and loop.is_running():
        loop.quit()
    
    sys.exit(0)


def parse_arguments():
    parser = argparse.ArgumentParser()

    # Increase verbosity with every occurance of -v
    parser.add_argument('-v', '--verbose', action='count', default=0)

    # Define for which player we're listening
    parser.add_argument('--player')

    return parser.parse_args()


def main():
    global loop, manager
    
    arguments = parse_arguments()

    # Initialize logging
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG,
                        format='%(name)s %(levelname)s %(message)s')

    # Logging is set by default to WARN and higher.
    # With every occurrence of -v it's lowered by one
    logger.setLevel(max((3 - arguments.verbose) * 10, 0))

    # Log the sent command line arguments
    logger.debug('Arguments received {}'.format(vars(arguments)))

    try:
        manager = Playerctl.PlayerManager()
        loop = GLib.MainLoop()

        manager.connect('name-appeared', lambda *args: on_player_appeared(*args, arguments.player))
        manager.connect('player-vanished', on_player_vanished)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        for player in manager.props.player_names:
            if arguments.player is not None and arguments.player != player.name:
                logger.debug('{player} is not the filtered player, skipping it'
                             .format(player=player.name)
                             )
                continue

            init_player(manager, player)

        logger.debug('Starting main loop')
        loop.run()
        
    except Exception as e:
        logger.error(f'Error in main: {e}')
        cleanup_resources()
        sys.exit(1)
    
    finally:
        # Asegurar limpieza en cualquier caso
        cleanup_resources()


if __name__ == '__main__':
    main()
