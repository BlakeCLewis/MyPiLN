--
-- Database: PiLN
--
-- --------------------------------------------------------
--
-- Table structure for table Profiles
-- ('INTEGER PRIMARY KEY' is aliased to rowid and is autoincremented)
CREATE TABLE IF NOT EXISTS profiles (
  run_id  INTEGER PRIMARY KEY,
  state   varchar(25) NOT NULL DEFAULT 'Staged',
  notes   text,
  p_param float NOT NULL,
  i_param float NOT NULL,
  d_param float NOT NULL,
  start_time timestamp NULL DEFAULT NULL,
  end_time   timestamp NULL DEFAULT NULL
);
-- --------------------------------------------------------
--
-- Table structure for table Firing
--
CREATE TABLE IF NOT EXISTS firing (
  run_id     int(11) NOT NULL,
  segment    int(11) NOT NULL DEFAULT 0,
  dt         timestamp NOT NULL DEFAULT CURRENT_DATATIME,
  set_temp   decimal(8,2) NOT NULL,
  temp       decimal(8,2) NOT NULL,
  int_temp   decimal(8,2) DEFAULT NULL,
  pid_output decimal(8,2) NOT NULL,
  PRIMARY KEY(run_id,segment,dt),
  FOREIGN KEY(run_id) REFERENCES profiles(run_id)
);
-- --------------------------------------------------------
--
-- Table structure for table Segments
--
CREATE TABLE IF NOT EXISTS segments (
  run_id   int(11) NOT NULL,
  segment  int(11) NOT NULL,
  set_temp int(11) NOT NULL,
  rate     int(11) NOT NULL,
  hold_min int(11) NOT NULL,
  int_sec  int(11) NOT NULL,
  start_time timestamp NULL DEFAULT NULL,
  end_time   timestamp NULL DEFAULT NULL,
  PRIMARY KEY (run_id,segment),
  FOREIGN KEY(run_id) REFERENCES profiles(run_id)
);
