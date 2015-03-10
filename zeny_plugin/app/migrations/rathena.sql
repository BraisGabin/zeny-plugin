CREATE TABLE IF NOT EXISTS `login` (
  `account_id` int(11) unsigned NOT NULL auto_increment,
  `userid` varchar(23) NOT NULL default '',
  `user_pass` varchar(32) NOT NULL default '',
  `sex` enum('M','F','S') NOT NULL default 'M',
  `email` varchar(39) NOT NULL default '',
  `group_id` tinyint(3) NOT NULL default '0',
  `state` int(11) unsigned NOT NULL default '0',
  `unban_time` int(11) unsigned NOT NULL default '0',
  `expiration_time` int(11) unsigned NOT NULL default '0',
  `logincount` mediumint(9) unsigned NOT NULL default '0',
  `lastlogin` datetime NOT NULL default '0000-00-00 00:00:00',
  `last_ip` varchar(100) NOT NULL default '',
  `birthdate` DATE NOT NULL DEFAULT '0000-00-00',
  `character_slots` tinyint(3) unsigned NOT NULL default '0',
  `pincode` varchar(4) NOT NULL DEFAULT '',
  `pincode_change` int(11) unsigned NOT NULL DEFAULT '0',
  `bank_vault` int(11) NOT NULL DEFAULT '0',
  `vip_time` int(11) unsigned NOT NULL default '0',
  `old_group` tinyint(3) NOT NULL default '0',
  PRIMARY KEY  (`account_id`),
  KEY `name` (`userid`)
) ENGINE=InnoDB AUTO_INCREMENT=2000000;

CREATE TABLE IF NOT EXISTS `char` (
  `char_id` int(11) unsigned NOT NULL auto_increment,
  `account_id` int(11) unsigned NOT NULL default '0',
  `char_num` tinyint(1) NOT NULL default '0',
  `name` varchar(30) NOT NULL DEFAULT '',
  `class` smallint(6) unsigned NOT NULL default '0',
  `base_level` smallint(6) unsigned NOT NULL default '1',
  `job_level` smallint(6) unsigned NOT NULL default '1',
  `base_exp` bigint(20) unsigned NOT NULL default '0',
  `job_exp` bigint(20) unsigned NOT NULL default '0',
  `zeny` int(11) unsigned NOT NULL default '0',
  `str` smallint(4) unsigned NOT NULL default '0',
  `agi` smallint(4) unsigned NOT NULL default '0',
  `vit` smallint(4) unsigned NOT NULL default '0',
  `int` smallint(4) unsigned NOT NULL default '0',
  `dex` smallint(4) unsigned NOT NULL default '0',
  `luk` smallint(4) unsigned NOT NULL default '0',
  `max_hp` mediumint(8) unsigned NOT NULL default '0',
  `hp` mediumint(8) unsigned NOT NULL default '0',
  `max_sp` mediumint(6) unsigned NOT NULL default '0',
  `sp` mediumint(6) unsigned NOT NULL default '0',
  `status_point` int(11) unsigned NOT NULL default '0',
  `skill_point` int(11) unsigned NOT NULL default '0',
  `option` int(11) NOT NULL default '0',
  `karma` tinyint(3) NOT NULL default '0',
  `manner` smallint(6) NOT NULL default '0',
  `party_id` int(11) unsigned NOT NULL default '0',
  `guild_id` int(11) unsigned NOT NULL default '0',
  `pet_id` int(11) unsigned NOT NULL default '0',
  `homun_id` int(11) unsigned NOT NULL default '0',
  `elemental_id` int(11) unsigned NOT NULL default '0',
  `hair` tinyint(4) unsigned NOT NULL default '0',
  `hair_color` smallint(5) unsigned NOT NULL default '0',
  `clothes_color` smallint(5) unsigned NOT NULL default '0',
  `weapon` smallint(6) unsigned NOT NULL default '0',
  `shield` smallint(6) unsigned NOT NULL default '0',
  `head_top` smallint(6) unsigned NOT NULL default '0',
  `head_mid` smallint(6) unsigned NOT NULL default '0',
  `head_bottom` smallint(6) unsigned NOT NULL default '0',
  `robe` SMALLINT(6) UNSIGNED NOT NULL DEFAULT '0',
  `last_map` varchar(11) NOT NULL default '',
  `last_x` smallint(4) unsigned NOT NULL default '53',
  `last_y` smallint(4) unsigned NOT NULL default '111',
  `save_map` varchar(11) NOT NULL default '',
  `save_x` smallint(4) unsigned NOT NULL default '53',
  `save_y` smallint(4) unsigned NOT NULL default '111',
  `partner_id` int(11) unsigned NOT NULL default '0',
  `online` tinyint(2) NOT NULL default '0',
  `father` int(11) unsigned NOT NULL default '0',
  `mother` int(11) unsigned NOT NULL default '0',
  `child` int(11) unsigned NOT NULL default '0',
  `fame` int(11) unsigned NOT NULL default '0',
  `rename` SMALLINT(3) unsigned NOT NULL default '0',
  `delete_date` INT(11) UNSIGNED NOT NULL DEFAULT '0',
  `moves` int(11) unsigned NOT NULL DEFAULT '0',
  `unban_time` int(11) unsigned NOT NULL default '0',
  `font` tinyint(3) unsigned NOT NULL default '0',
  `uniqueitem_counter` int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (`char_id`),
  UNIQUE KEY `name_key` (`name`),
  KEY `account_id` (`account_id`),
  KEY `party_id` (`party_id`),
  KEY `guild_id` (`guild_id`),
  KEY `online` (`online`)
) ENGINE=MyISAM AUTO_INCREMENT=150000;

CREATE TABLE IF NOT EXISTS `storage` (
  `id` int(11) unsigned NOT NULL auto_increment,
  `account_id` int(11) unsigned NOT NULL default '0',
  `nameid` smallint(5) unsigned NOT NULL default '0',
  `amount` smallint(11) unsigned NOT NULL default '0',
  `equip` int(11) unsigned NOT NULL default '0',
  `identify` smallint(6) unsigned NOT NULL default '0',
  `refine` tinyint(3) unsigned NOT NULL default '0',
  `attribute` tinyint(4) unsigned NOT NULL default '0',
  `card0` smallint(5) unsigned NOT NULL default '0',
  `card1` smallint(5) unsigned NOT NULL default '0',
  `card2` smallint(5) unsigned NOT NULL default '0',
  `card3` smallint(5) unsigned NOT NULL default '0',
  `expire_time` int(11) unsigned NOT NULL default '0',
  `bound` tinyint(3) unsigned NOT NULL default '0',
  `unique_id` bigint(20) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id`),
  KEY `account_id` (`account_id`)
) ENGINE=MyISAM;

CREATE TABLE `item_db_re` (
  `id` smallint(5) unsigned NOT NULL DEFAULT '0',
  `name_english` varchar(50) NOT NULL DEFAULT '',
  `name_japanese` varchar(50) NOT NULL DEFAULT '',
  `type` tinyint(2) unsigned NOT NULL DEFAULT '0',
  `price_buy` mediumint(8) unsigned DEFAULT NULL,
  `price_sell` mediumint(8) unsigned DEFAULT NULL,
  `weight` smallint(5) unsigned NOT NULL DEFAULT '0',
  `atk:matk` varchar(11) DEFAULT NULL,
  `defence` smallint(5) unsigned DEFAULT NULL,
  `range` tinyint(2) unsigned DEFAULT NULL,
  `slots` tinyint(2) unsigned DEFAULT NULL,
  `equip_jobs` int(10) unsigned DEFAULT NULL,
  `equip_upper` tinyint(2) unsigned DEFAULT NULL,
  `equip_genders` tinyint(1) unsigned DEFAULT NULL,
  `equip_locations` mediumint(7) unsigned DEFAULT NULL,
  `weapon_level` tinyint(1) unsigned DEFAULT NULL,
  `equip_level` varchar(10) DEFAULT NULL,
  `refineable` tinyint(1) unsigned DEFAULT NULL,
  `view` smallint(5) unsigned DEFAULT NULL,
  `script` text,
  `equip_script` text,
  `unequip_script` text,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM;

# etc
REPLACE INTO `item_db_re` VALUES (501,'Red_Potion','Red Potion',0,50,NULL,70,NULL,NULL,NULL,NULL,0xFFFFFFFF,63,2,NULL,NULL,NULL,NULL,NULL,'itemheal rand(45,65),0;',NULL,NULL);
REPLACE INTO `item_db_re` VALUES (502,'Orange_Potion','Orange Potion',0,200,NULL,100,NULL,NULL,NULL,NULL,0xFFFFFFFF,63,2,NULL,NULL,NULL,NULL,NULL,'itemheal rand(105,145),0;',NULL,NULL);
REPLACE INTO `item_db_re` VALUES (503,'Yellow_Potion','Yellow Potion',0,550,NULL,130,NULL,NULL,NULL,NULL,0xFFFFFFFF,63,2,NULL,NULL,NULL,NULL,NULL,'itemheal rand(175,235),0;',NULL,NULL);
REPLACE INTO `item_db_re` VALUES (504,'White_Potion','White Potion',0,1200,NULL,150,NULL,NULL,NULL,NULL,0xFFFFFFFF,63,2,NULL,NULL,NULL,NULL,NULL,'itemheal rand(325,405),0;',NULL,NULL);
REPLACE INTO `item_db_re` VALUES (505,'Blue_Potion','Blue Potion',0,5000,NULL,150,NULL,NULL,NULL,NULL,0xFFFFFFFF,63,2,NULL,NULL,NULL,NULL,NULL,'itemheal 0,rand(40,60);',NULL,NULL);
REPLACE INTO `item_db_re` VALUES (506,'Green_Potion','Green Potion',0,40,NULL,70,NULL,NULL,NULL,NULL,0xFFFFFFFF,63,2,NULL,NULL,NULL,NULL,NULL,'sc_end SC_Poison; sc_end SC_Silence; sc_end SC_Blind; sc_end SC_Confusion;',NULL,NULL);

# Weapons
REPLACE INTO `item_db_re` VALUES (1101,'Sword','Sword',5,100,NULL,500,'25',NULL,1,3,0x000654E3,63,2,2,1,'2',1,2,NULL,NULL,NULL);
REPLACE INTO `item_db_re` VALUES (1373,'Brood_Axe_C','Refined Bloody Axe',5,2,NULL,0,'205',NULL,1,0,0x000444A2,63,2,34,4,'0',0,7,'bonus bStr,20; bonus bMatkRate,20; bonus bAspdRate,5;',NULL,NULL);

# Armors
REPLACE INTO `item_db_re` VALUES (2301,'Cotton_Shirt','Cotton Shirt',4,10,NULL,100,NULL,10,NULL,0,0xFFFFFFFF,63,2,16,NULL,'0',1,0,NULL,NULL,NULL);

# Pet Eggs
REPLACE INTO `item_db_re` VALUES (9001,'Poring_Egg','Poring Egg',7,20,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);

# Pet Armors
REPLACE INTO `item_db_re` VALUES (10001,'Skull_Helm','Skull Helm',8,20,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);

# Shadow Gears
REPLACE INTO `item_db_re` VALUES (24001,'T_DEX1_Weapon_Shadow','T DEX1 Weapon Shadow',12,10,NULL,0,NULL,NULL,NULL,0,0xFFFFFFFF,63,2,131072,NULL,'1',NULL,NULL,'bonus bDex,1;',NULL,NULL);
