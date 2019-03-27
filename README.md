# Syllabus
Time and memory tracking task manager for Machine Learning applications

![Print It!](https://github.com/thetianshuhuang/syllabus/blob/master/basic.png)

## Dependencies
- Python 3
- print
- ansiwrap

## Requirements
- min terminal width of 66 columns
- ANSI color support

# Usage

## The Task Class
The ```Task``` class is the core of ```Syllabus```. Only one task should ever be created from scratch in any program; all other tasks should be spawned off of this task using ```subtask```.

### Parameters
- ```name```: str; name of the task
- ```desc```: str; task description
- ```mp```: bool; True if multiprocessing should be enabled. This creates a multiprocessing managed queue, which allows the queue to be shared with other processes; however, this operation requires creation of a dedicated process, and has a significant memory cost. Therefore, the ```mp``` flag should not be enabled unless multiprocessing is to be used.

### Core Methods
- ```start(name=None, desc=None)```: start the task (sets the start time). If name or description are not None, updates the task's name and description.
- ```done(*objects, name=None, desc=None, nowait=False)```: mark the task as done (sets the end time).
	- ```name```, ```desc```: name and description; if not None, updates the name and description.
	- ```*objects```: list of objects. Adds the memory footprints of the objects, and stores it in order to track memory usage.
	- ```nowait```: is only considered if the task is a root task. If nowait is set to True, the program continues immediately; if nowait is set to False, the method blocks until the task's accountant finishes processing all messages.
- ```subtask(name='Child Task', desc=None) -> Task```: create a subtask. This method should always be used when creating new tasks, since it passes the parent task's reporting queue on to the child.
	- ```name```: subtask name
	- ```desc```: subtask description

### Status, Reporting
- ```info(msg)```: send message; ```msg``` can be arbitrary type, as long as ```msg``` can be turned into a string with ```str()```)
- ```print(msg)```: alias for ```info```
- ```error(e)```: send error. ```e``` does not have to be an Exception.
- ```warn(e)```: send warning. ```e``` does not have to be a Warning.
- ```runtime() -> float```: get current runtime.
- ```status() -> (int, int)```: get progress as (complete tasks, total tasks)
- ```progress() -> float```: get progress as (complete tasks / total tasks)
- ```add_task(n)```: add ```n``` tasks to the task counter
- ```add_progress(n)```: mark an additional ```n``` tasks as completed

### Multithreading
- ```pool(target, args, shared_args=[], shared_kwargs={}, reducer=None, recursive=True, split=2, name='Child Task Thread', threads=None, process=False)```: Create a thread pool.
	- ```target```: target function
	- ```args```: list of args to pass in
	- ```shared_args```, ```shared_kwargs```: shared arguments to pass to all threads
	- ```reducer(retval[])```: if a function is passed, is used to combine results. Should take in a list of results (as returned by ```target```) and return a combined result.
	- ```recursive```: reduce recursively?
	- ```split```: if ```recursive```, how many entries per reduce?
	- ```name```: child task default name
	- ```threads```: number of threads; if ```None```, uses ```cpu_count()``` instead

### Multiprocessing
- ```pool(target, args, shared_args=None, shared_init=None, reducer=None, recursive=True, split=2, name='Child Task Process', cores=None)```: Create a process pool.
	- ```target```: target function
	- ```args```: list of args to pass in
	- ```shared_args```: shared arguments to pass to all threads
	- ```shared_init```: initializer for shared args
	- ```reducer(retval[])```: if a function is passed, is used to combine results. Should take in a list of results (as returned by ```target```) and return a combined result.
	- ```recursive```: reduce recursively?
	- ```split```: if ```recursive```, how many entries per reduce?
	- ```name```: child task default name
	- ```cores```: number of cores; if ```None```, uses ```cpu_count()``` instead

## App

### Parameters
- ```BasicTaskApp(*args, refresh_rate=20, **kwargs)```: basic app with a updating output
	- ```refresh_rate```: output refresh rate, in Hz
	- Extends ```Task```; configuration options ```*args``` and ```**kwargs``` are passed on.

- ```InteractiveTaskApp(*args, refresh_rate=20, **kwargs)```: more sophisticated terminal app with keyboard controls
	- ```refresh_rate```: output refresh rate, in Hz
	- Extends ```Task```; configuration options ```*args``` and ```**kwargs``` are passed on.

- ```TaskViewer(file)```: viewer for saved task trees.
	- ```file```: input filename to open and parse
	- Methods:
		- ```print()```: print tree (same format as ```BasicTaskApp```)
		- ```save(file, color=False)```: save rendered output to file
			- ```file```: output filename
			- ```color```: if False, ANSI escape sequences are stripped before saving 
