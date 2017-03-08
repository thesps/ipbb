from __future__ import print_function

# Modules
import click
import os
import ipbb
import subprocess

# Elements
from . import kProjAreaCfgFile, kProjDir
from .common import DirSentry

from os.path import join, split, exists, splitext
from ..tools.common import SmartOpen


#------------------------------------------------------------------------------
def _getprojects(env):

  if not exists(env.proj):
    raise click.ClickException("Directory '%s' does not exist." % env.proj )

  '''Returns the list of existing projects'''
  return [ lProj for lProj in next(os.walk(env.proj))[1] if exists( join( env.proj, lProj, kProjAreaCfgFile ) ) ]
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
@click.group()
def proj():
  pass
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def _validateComponent(ctx, param, value):
  lSeparators = value.count(':')
  # Validate the format
  if lSeparators > 1:
    raise click.BadParameter('Malformed component name : %s. Expected <module>:<component>' % value)
  
  return tuple(value.split(':'))
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# TODO: move the list of supported products somewhere else
@proj.command()
@click.argument('kind', type=click.Choice(['vivado', 'sim']))
@click.argument('projname')
@click.argument('component', callback=_validateComponent)
@click.option('-t', '--topdep', default='top.dep', help='Top-level dependency file')
@click.pass_obj
def create( env, kind, projname, component, topdep ):
  '''Create a new project area

    Creates a new area of name PROJNAME of kind KIND 

    PROJAREA: Name of the new project area

    KIND: Area kind, choices: vivado, sim
    
    COMPONENT: Component contaning the top-level
  '''
  #------------------------------------------------------------------------------
  # Must be in a build area
  if env.workPath is None:
    raise click.ClickException('Build area root directory not found')
  #------------------------------------------------------------------------------

  #------------------------------------------------------------------------------
  lProjAreaPath = join( env.workPath, kProjDir, projname )
  if exists(lProjAreaPath):
    raise click.ClickException('Directory %s already exists' % lProjAreaPath)
  #------------------------------------------------------------------------------

  #------------------------------------------------------------------------------
  from ..depparser.Pathmaker import Pathmaker
  lPathmaker = Pathmaker(env.src, 0)
  lTopPackage, lTopComponent = component
  lTopDepPath = lPathmaker.getPath( lTopPackage, lTopComponent, 'include', topdep )
  if not exists(lTopDepPath):
    raise click.ClickException('Top-level dependency file %s not found' % lTopDepPath)
  #------------------------------------------------------------------------------

  # Build source code directory
  os.makedirs(lProjAreaPath)

  lCfg = {
    'toolset': kind,
    'topPkg': lTopPackage,
    'topCmp': lTopComponent,
    'topDep': topdep,
    'name':   projname

  }
  with SmartOpen( join(lProjAreaPath, kProjAreaCfgFile) ) as lProjFile:
    import json
    json.dump(lCfg, lProjFile.file, indent=2)

  click.secho('Project area %s created' % projname,fg='green')
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
@proj.command()
@click.pass_obj
def ls( env ):
  '''Lists all available project areas
  '''
  lProjects = _getprojects(env)
  print ( 'Main work area:', env.workPath )
  print ( 'Projects areas:', ', '.join( [ lProject + ('*' if lProject == env.project else '') for lProject in lProjects ] ) )
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
@proj.command()
@click.argument( 'projname' )
@click.pass_obj
def printpath( env, projname ):
  
  lProjects = _getprojects(env)

  if projname not in lProjects:
    raise click.ClickException('Requested work area not found. Available areas: %s' % ', '.join(lProjects))

  print ( os.path.join( env.proj, projname ))
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
@proj.command()
@click.argument( 'projname' )
@click.pass_obj
def cd( env, projname ):
  '''Changes current working directory (command line only)
  '''

  if projname[-1] == os.sep: projname = projname[:-1]
  lProjects = _getprojects(env)
  if projname not in lProjects:
    raise click.ClickException('Requested work area not found. Available areas: %s' % ', '.join(lProjects))

  with DirSentry( join(env.proj, projname) ) as lSentry:
    env._autodetect()

  os.chdir(join(env.proj, projname))
  print ( "New current directory %s" % os.getcwd() )
#------------------------------------------------------------------------------